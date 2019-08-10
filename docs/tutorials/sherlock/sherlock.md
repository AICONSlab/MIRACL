## Running MIRACL commands on Sherlock (Stanford supercomputer)
### Copy Data
    $ scp

### Login to Sherlock
    $ ssh -XY username@login.stanford.edu

### Start interactive session
    $ sdev

### Start singularity with binded data
    $ cd $SCRATCH
    $ singularity shell -B MIRACLextra:/data /home/mgoubran/miracl_latest.sif

### Run command
    miracl flow reg_clar -f input -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"
