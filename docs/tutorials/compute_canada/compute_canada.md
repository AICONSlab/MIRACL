## Running MIRACL commands on Compute Canada

This tutorial highlights the registration workflow but 
a similar approach applies to other commands 

When using Compute Canada, the Docker image for MIRACL can be used in Singularity. The following instructions are based on the steps provided on the Compute Canada wiki.

### Copy your data to Compute Canada
For example, to copy a folder called "input_clar" containing tiff files for registration to the Allen atlas:
    
    $ scp -r input_clar niagara.computecanada.edu:/scratch/{username}/.

### Login the same to Compute Canada Server

    $ ssh -XY username@niagara.computecanada.edu

### Setting up and using MIRACL

Load the specific Singularity module you would like to use (in this case, Singularity 3.5)

    $ module load singularity/3.5

The generated image takes up a large amount of space, so move to the scratch directory to build and work with MIRACL

	$ cd $SCRATCH

Pull (download) the Singularity container:

    $ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest

Start singularity with binded data

    $ singularity shell miracl_latest.sif

Within the shell, load the GUI

    > miraclGUI

Or use command line, for example run miracl's CLARITY registration workflow on the directory that was copied over

    > miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"
