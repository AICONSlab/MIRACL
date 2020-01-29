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
        ''' Add paths to PATH environment variable prior to running the function.
        '''
        for command in self.command_paths.keys():
            if os.path.isdir(self.command_paths[command]):
                os.environ['PATH'] += os.pathsep + self.command_paths[command]
                self.added_paths.append(self.command_paths[command])
            else:
                print('ERROR: %s is required to continue. Please install using the instructions on https://miracl.readthedocs.io/en/latest/install-local.html' \
                    % (command))
                sys.exit()

        # if ants is added, we have to include it in ANTSPATH
        if self.command_paths['ANTS'] in self.added_paths:
            os.environ['ANTSPATH'] += os.pathsep + self.command_paths['ANTS']

    def __exit__(self, exc_type, exc_value, traceback):
        for path in self.added_paths:  # remove all added PATH variables
            try:
                os.environ['PATH'] = os.environ['PATH'].replace(path, '')
            except ValueError:
                pass
