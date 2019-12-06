## Running MIRACL commands on Compute Canada

This tutorial highlights the registration workflow but 
a similar approach applies to other commands 

### Copy your data to Sherlock 
For example a folder called "input_clar" with tiff files for registration to Allen atlas:
    
    $ scp -r input_clar niagara.computecanada.edu:/scratch/users/username/. 

### Login to Sherlock
    $ ssh -XY username@niagara.computecanada.edu

### Start interactive session
    $ sdev

### Start singularity with binded data
    $ cd $SCRATCH
    $ singularity shell -B MIRACLextra:/data /home/mgoubran/miracl_latest.sif

### Run command
    miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"
