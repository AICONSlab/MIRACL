## Running MIRACL commands on Compute Canada

This tutorial highlights the registration workflow but 
a similar approach applies to other commands 

When using Compute Canada, the Docker image for MIRACL can be used in Singularity. The following instructions are based on the steps provided on the Compute Canada wiki.

### Copy your data to Compute Canada
For example, to copy a folder called "input_clar" containing tiff files for registration to the Allen atlas:
    
    $ scp -r input_clar niagara.computecanada.edu:/home/{username}/scratch/. 

### Login the same to Compute Canada Server

    $ ssh -XY username@niagara.computecanada.edu

### Setting up and using MIRACL

Load the specific Singularity module you would like to use (in this case, Singularity 3.5)

    $ module load singularity/3.5

The generated image takes up a large amount of space, so move to the scratch directory to build and work with MIRACL

	$ cd $SCRATCH

Although MIRACL is stored as a Docker image, an image can be built in Singularity by calling

	$ singularity build miracl.sif docker://mgoubran/miracl

Start singularity with binded data

    $ singularity shell miracl.sif

Within the shell, try loading the GUI

	> miraclGUI

To test the shell, try running miracl's CLARITY registration workflow on the directory that was copied over

    > miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"
