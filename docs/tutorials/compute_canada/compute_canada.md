# Running MIRACL on Compute Canada

This tutorial highlights the registration workflow but a similar approach
applies to other commands.

When using Compute Canada, MIRACL can be used as a Singularity container. The 
following instructions are based on the steps provided on the Compute Canada 
wiki.

## Copy your data to Compute Canada

For example, to copy a folder called `input_clar` containing tiff files you
want to register to the Allen Atlas use:

```
$ scp -r input_clar niagara.computecanada.edu:/scratch/<username>/.
```

or 

```
$ rsync -avPhz input_clar <username>@niagara.computecanada.edu:/scratch/<username>/.
```
 
## Log in to Compute Canada server

Log in to the Compute Canada server you copied your data to:

```
$ ssh -XY <username>@niagara.computecanada.edu
```

## Setting up and using MIRACL

Load the specific Singularity module you would like to use (e.g. Singularity 3.5):

```
$ module load singularity/3.5
```

> Not specifying the version will load the latest version available on your node

Since MIRACL will take up a significant amount of space, it is recommended to
download and work with the MIRACL Singularity container in the scratch
directory. First, navigate there:

```
$ cd $SCRATCH
```

Then pull (download) the Singularity container:

```
$ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest
```

Start the MIRACL Singularity container with the default folders mounted:

```
$ singularity shell miracl_latest.sif bash
```

Singularity will automatically mount your scratch folder to your container.
If you need to mount a specific directory into specific location, use the 
following:

```
$ singularity shell -B <location_outside_container>/<source_mount>:<location_in_container>/<target_mount> miracl_latest.sif bash
```

Once you are logged in to the container, load the GUI from the shell:

```
$ miraclGUI
```

> Please consult our [Troubleshooting](../../troubleshooting.md) section if you experience problems with 
opening MIRACL's GUI on Compute Canada

Or use MIRACL from the command line. For example, run MIRACL's CLARITY 
registration workflow on the folder that you copied over previously:

```
$ miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"
```

> If you have a particular Singularity container of MIRACL that you want to use
on Compute Canada, just copy it to the servers directly using e.g. `scp` or `sync`
instead of pulling (downloading) the latest version of MIRACL from the 
Singularity registry

---

[<- back to tutorials](../../tutorials.md)
