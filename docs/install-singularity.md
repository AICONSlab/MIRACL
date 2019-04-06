# Singularity Install

Unlike Docker, Singularity is well suited to run in a cluster environment. In fact, if
the Docker image for this repository is provided on Docker hub, you could just pull
and use it. First, log in to the cluster:

```bash
ssh -XY username@login.stanford.edu
```

Then grab a development node. If you try pulling from the login node, you will use a ton of memory building the SIF image,
and the process will be killed (in other words, it won't work).


```bash
$ sdev
```

Once you have your node, you can then pull the container:

```bash
$ singularity pull docker://mgoubran/miracl:dev
```

If you want to give it a custom name, you can do the following (and make sure you
are sitting in your $SCRATCH directory so you don't take up all the space in $HOME.

```
$ cd $SCRATCH
$ singularity build miracl.sif docker://mgoubran/miracl:dev
```


## Interaction

To shell into the image:

```
$ singularity shell miracl.sif
```

Bind a data directory to it

```
$ singularity shell -B data:/data miracl.sif
```

## Testing

I'll do my best to test, although I'm not familiar with this tool. First, if you
call `miracl` a GUI comes up, but there are bugs with getting the correct path
to the scripts, so I'll run these from the command line. First clone the input
data:

```bash
$ git clone https://github.com/vsoch/MIRACLextra
```

Then try running the registration.

```bash
/code/miracl/flow/miracl_workflow_registration_clarity-allen_wb.sh -f $CLARITY_DIR
```
(This doesn't work)
