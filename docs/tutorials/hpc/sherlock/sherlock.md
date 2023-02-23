# Running MIRACL commands on Sherlock (Stanford supercomputer)

This tutorial highlights the registration workflow but a similar approach 
applies to other commands.

## Setting up MIRACL (first time) 

Login to Sherlock

```
$ ssh -Y username@sherlock.stanford.edu
```

Start interactive session:

```
$ sdev
```

Move to your scratch folder:

```
$ cd SCRATCH
```

Pull (download) Singularity container:

```
$ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest
```

> If you have a particular Singularity container of MIRACL that you want to use
on Sherlock, just copy it to the servers directly using e.g. `scp` or `rsync`
instead of pulling (downloading) the latest version of MIRACL from the 
Singularity registry

## Copying your data to Sherlock 

Copy a folder called, e.g. `input_clar` with tiff files that you want to 
register to Allen Atlas using `scp`:
    
```
$ scp -r input_clar sherlock.stanford.edu:/scratch/users/<username>/clarity_registration/.
```

or `rsync`:

```
$ rsync -avPhz input_clar sherlock.stanford.edu:/scratch/users/<username>/clarity_registration/.
```

> Make sure to replace \<username\> with your Sherlock username

## Running MIRACL in an interactive session

For quick jobs that don't require much resources you can login to Sherlock:

```
$ ssh -Y username@sherlock.stanford.edu
```

Move to your scratch folder:

```
$ cd SCRATCH
```

Start interactive session:

```
$ sdev
```
    
Start Singularity with binded data:

```
$ singularity shell miracl_latest.sif bash
```

Within the shell, load the GUI:

```
$ miraclGUI
```

Or use the command-line:

```
$ miracl lbls stats -h
```

> Please consult our [Troubleshooting](../../../troubleshooting.md) section if you experience problems with 
opening MIRACL's GUI on Sherlock

## Running SBATCH jobs

If you want to run jobs with specific resources for larger, longer jobs (e.g. 
running the registration workflow) you can do the following:

First get the data orientation (please check the registration tutorial for 
setting orientation):

```
$ miracl conv set_orient
```

After setting the orientation, a file called `ort2std.txt` will be created that 
might look like this:

```
$ cat ort2std.txt
tifdir=/scratch/users/username/clarity_registration/input_clar
ortcode=ARS
```

Use that orientation code (`ARS`) in your registration workflow.

First check the workflow arguments:

```
$ miracl flow reg_clar -h
```

Assuming you wanted to run this command with the following arguments, for 
example on your data:

```
$ miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"
```

Create an sbatch script named, for example `reg_job.sbatch` and paste the 
following lines:

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

> Note that the miracl function call comes after invoking the Singularity call
`singularity exec ${SCRATCH}/miracl_latest.sif` and that full file paths were 
used for the `.sif` container and the the input data

This sample job (called: `clar_reg`) asks for 5 hours, 12 cpus and 32G of 
memory on one node. Adjust the requested resources based on the job you are 
submitting.

Next submit the sbatch script:

```
$ sbatch reg_job.sbatch
```

To check on the status of your submitted job use:

```
$ squeue -u $USER
```
    
> For more resources on SLURM sbatch jobs check Stanford's tutorials on
[submitting](https://www.sherlock.stanford.edu/docs/getting-started/submitting/)
and [running](https://www.sherlock.stanford.edu/docs/user-guide/running-jobs/)
jobs on Sherlock

---

[<- back to tutorials](../../../tutorials.md)
