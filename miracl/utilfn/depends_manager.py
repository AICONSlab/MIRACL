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

        # dictionary of symbolic links, and the paths that add them
        self.symlinks = dict(ants_miracl_clar=os.path.join(DEPENDS_DIR, "ants/antsRegistrationMIRACL.sh"),
                             ants_miracl_mr=os.path.join(DEPENDS_DIR, "ants/antsRegistrationMIRACL_MRI.sh"))
        self.added_links = []

    def __enter__(self):
        ''' Add paths to PATH environment variable prior to running the function.
        '''
        for command in self.command_paths.keys():
            try:
                subprocess.check_call(['which', command])
            except subprocess.CalledProcessError:  # if the command doesnt exist, add it to the path
                if os.path.isdir(self.command_paths[command]):
                    os.environ['PATH'] += os.pathsep + self.command_paths[command]
                    self.added_paths.append(self.command_paths[command])
                else:
                    print('ERROR: %s is required to continue. Please install using the instructions on https://miracl.readthedocs.io/en/latest/install-local.html' \
                        % (command))
                    sys.exit()

        # if ants is added, we have to include it in ANTSPATH
        if self.command_paths['ANTS'] in self.added_paths:
            if 'ANTSPATH' in os.environ.keys():
                os.environ['ANTSPATH'] += os.pathsep + self.command_paths['ANTS']
            else:
                os.environ['ANTSPATH'] = self.command_paths['ANTS']

        # create the symbolic links here
        try:
            for link in self.symlinks.keys():
                if not os.path.islink(os.path.join(self.command_paths['ANTS'], link)):
                    os.symlink(self.symlinks[link], os.path.join(self.command_paths['ANTS'], link))
                    self.added_links.append(os.path.join(self.command_paths['ANTS'], link))
        except OSError:  # error comes up with readonly system (e.g. Docker)
            print('WARNING: unable to add symbolic link for %s. Please ensure that symbolic link has been set externally (i.e. in Dockerfile)' % (link))

    def __exit__(self, exc_type, exc_value, traceback):
        for path in self.added_paths:  # remove all added PATH variables
            try:
                os.environ['PATH'] = os.environ['PATH'].replace(path, '')
            except ValueError:
                pass
        
        # remove symlinks
        for link in self.added_links:
            if os.path.islink(link):
                os.unlink(link)

        # remove ANTSPATH if it was set
        if 'ANTSPATH' in os.environ.keys() and self.command_paths['ANTS'] in self.added_paths:
            os.environ['ANTSPATH']  = os.environ['PATH'].replace(self.command_paths['ANTS'], '')
