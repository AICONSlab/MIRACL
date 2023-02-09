## Running MIRACL commands on Sherlock (Stanford supercomputer)

This tutorial highlights the registration workflow but 
a similar approach applies to other commands 

### Setting up MIRACL (first time) 
You can skip this section if you ran through the Singularity install

Login to Sherlock

    $ ssh -Y username@sherlock.stanford.edu

Start interactive session

    $ sdev

Move to your scratch folder

    $ cd SCRATCH

Pull (download) Singularity container 

    $ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest

### Copying your data to Sherlock 
For example a folder called `input_clar` with tiff files for registration to Allen atlas:
(replace username with your sherlock username)
    
    $ scp -r input_clar sherlock.stanford.edu:/scratch/users/username/clarity_registration/.

### Running MIRACL in an interactive session
For quick jobs that don't require much resources

Login to Sherlock

    $ ssh -Y username@sherlock.stanford.edu

Move to your scratch folder

    $ cd SCRATCH

Start interactive session

    $ sdev
    
 Start singularity with binded data

    $ singularity shell miracl_latest.sif bash

Within the shell, load the GUI  

    > miraclGUI

Or use command line

    > miracl lbls stats -h

### Running SBATCH jobs
If you want to run jobs with specific resources for larger, longer jobs

For example if you want to run the registration workflow, first get the data orientation 
(please check the registration tutorial for setting orientation)

    > miracl conv set_orient

After setting the orientation a file called ``ort2std.txt`` will be created that might look like this:

    > cat ort2std.txt

```text
tifdir=/scratch/users/username/clarity_registration/input_clar
ortcode=ARS
```

Use that orientation code `ARS` in your registration workflow 

First check the workflow arguments

    > miracl flow reg_clar -h

Assuming you wanted to run this command with the following arguments for example on your data:

    miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

Create an sbatch script, for example `reg_job.sbatch` with the following lines:

```bash
#!/bin/bash
#SBATCH --job-name=clar_reg
#SBATCH --ntasks=1
#SBATCH --time=05:00:00
#SBATCH --cpus-per-task=12
#SBATCH --mem=32G

module load singularity

singularity exec ${SCRATCH}/miracl_latest.sif miracl flow reg_clar -f ${SCRATCH}/clarity_registration/input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

```

Notice the miracl function call came after: `singularity exec ${SCRATCH}/miracl_latest.sif`

And we added full path of the input data

This sample job (called: clar_reg) asks for 5 hours, 12 cpus and 32G of memory in one node.
Adjust the requested resources based on the job you are submitting.

Then submit the sbatch script

    $ sbatch reg_job.sbatch

Check on submitted job

    $ squeue -u $USER
    
    
#### For more resources on slurm sbatch jobs check these pages

[sherlock submitting jobs](https://www.sherlock.stanford.edu/docs/getting-started/submitting/)

[sherlock running jobs](https://www.sherlock.stanford.edu/docs/user-guide/running-jobs/)
