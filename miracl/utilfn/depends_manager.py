import os
import sys
import subprocess

from miracl import DEPENDS_DIR

class add_paths():
    """ Context manager to add necessary paths to PATH environment variable. Files will be removed after use
    """
    def __init__(self):
        # create dictionary of paths that will temporarily be added to the PATH env variable
        self.command_paths = dict(ANTS=os.path.join(DEPENDS_DIR, "ants"),
                                  c3d=os.path.join(DEPENDS_DIR, "c3d/bin"))
        self.added_paths = []  # empty list for all paths to be added
    
    def __enter__(self):
        for command in self.command_paths.keys():
            # if command doesnt have path, add path to env variable
            try:
                subprocess.check_call(["which", command])
            except subprocess.CalledProcessError: # command was not found
                os.environ['PATH'] += os.pathsep + self.command_paths[command]
                self.added_paths.append(self.command_paths[command])

    def __exit__(self, exc_type, exc_value, traceback):
        for path in self.added_paths:  # remove all added PATH variables
            try:
                os.environ['PATH'] = os.environ['PATH'].replace(path, '')
            except ValueError:
                pass
