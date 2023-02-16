# Singularity installation for (SLURM) cluster environments

Unlike Docker, Singularity is well suited to run in a cluster environment
(like Sherlock at Stanford or Compute Canada). We provide the latest version 
of MIRACL as a Singularity container that can be conveniently pulled from cloud 
storage.

## Download container

First, log in to the cluster:

```
$ ssh -Y username@cluster
```

`cluster` could be "sherlock.stanford.edu" or "cedar.computecanada.ca" 
for example.

Once logged in, change the directory to your scratch space and pull (download) 
the Singularity container:

```
$ cd $SCRATCH
$ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest
```

## Interaction

To shell into the container use:

```
$ singularity shell miracl_latest.sif bash
```

Use the `-B` flag to bind a data directory to the container:

```
$ singularity shell -B /data:/data miracl_latest.sif bash
```

> For running functions on clusters please check our Singularity tutorials for
[Compute Canada](./tutorials/compute_canada/compute_canada.md) and
[Sherlock](./tutorials/sherlock/sherlock.md)

## Troubleshooting

Please refer to our [Troubleshooting](troubleshooting.md) section.
