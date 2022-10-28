# Singularity Install for SLURM clusters 

Unlike Docker, Singularity is well suited to run in a cluster environment (like Sherlock at Stanford or Compute Canada). We provide the latest version of MIRACL as a Singularity container that can be conveniently pulled from cloud storage. First, log in to the cluster:

    ssh -Y username@cluster

`cluster` could be "sherlock.stanford.edu" or "cedar.computecanada.ca" for example.

Once logged in, change the directory to your scratch space and pull (download) the Singularity container:

    $ cd $SCRATCH
    $ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest

### Interaction

To shell into the container use:

    $ singularity shell miracl_latest.sif

Use the `-B` flag to bind a data directory to the container:

    $ singularity shell -B data:/data miracl_latest.sif

**For running functions on clusters please check our [tutorials](tutorials.md).**

## Troubleshooting

### Q: Can I build a Singularity container from the latest MIRACL image on Docker Hub:

Absolutely! To do so, however, you will need to grab a development node after logging in to the cluster. If you try pulling from the login node, you will use a ton of memory building the SIF image,
and the process will be killed (in other words, it won't work).

    $ sdev

or 
   
    $ salloc

Once you have your node, you can then build the container:

    $ cd $SCRATCH
    $ singularity build miracl_latest.sif docker://mgoubran/miracl:latest

### Q: Processes that require TrackVis or Diffusion Toolkit are not working:

Because of their respective licenses, we could not include TackVis or Diffusion Toolkit in our Singularity container directly. Please download and install them on you host machine using their [installation guide](http://trackvis.org/docs/?subsect=installation).

### Q: I get the following error whenever I try to run the GUI from within the Singularity container on Compute Canada:

```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.
```

**If you want to use X11 follow the below workarounds. However, using VNC instead of X11 should solve this issue and result in performance improvements. Instructions on how to use VNC on Compute Canada can be found [here](https://docs.alliancecan.ca/wiki/VNC).**

### Login Nodes

Exit your Singularity container and start a VNC server (for 3600sec or more as required) on your login node:

```
vncserver -MaxConnectionTime 3600
```

The first time the VNC server is started you will prompted for a password (do not leave this blank). Once done, check if a X11 socket is available for your username:

```
ls -la /tmp/.X11-unix/
```

(If no socket is available for your username, log out and log back in to your login node)

Start another Singularity container and try to run `miraclGUI` again from within it.

### Compute Nodes

Exit your Singularity container and set an environment variable on your allocated compute node:

```
export XDG_RUNTIME_DIR=${SLURM_TMPDIR}
```

Start a VNC server:

```
vncserver
```

Start another Singularity container and try to run `miraclGUI` again from within it.
