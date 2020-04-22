# Singularity Install for SLURM clusters 

Unlike Docker, Singularity is well suited to run in a cluster environment (like Sherlock at Stanford or Compute Canada). In fact, if
the Docker image for this repository is provided on Docker hub, you could just pull
and use it. First, log in to the cluster:

    ssh -Y username@cluster

cluster could be "sherlock.stanford.edu" or "cedar.computecanada.ca" for example.

Then grab a development node. If you try pulling from the login node, you will use a ton of memory building the SIF image,
and the process will be killed (in other words, it won't work).

    $ sdev

or 
   
    $ salloc

Once you have your node, you can then build the container:

    $ cd $SCRATCH
    $ singularity build miracl_latest.sif docker://mgoubran/miracl:latest


## Interaction

To shell into the image:


    $ singularity shell miracl.sif


Bind a data directory to it

    $ singularity shell -B data:/data miracl.sif


#### For running functions on clusters please check our tutorials

