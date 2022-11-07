# Troubleshooting

If you cannot find an answer to your problem here, please open an issue on our [offical GitHub page](https://github.com/AICONSlab/MIRACL).

## Docker

### Q: The GUI (`miraclGUI`) is not working:

Access control might be enabled on your host machine. Change your `xhost` access control on your host machine (**not** within your Docker container). Exit the running Docker container and type:

```
xhost +
```

Log back in to your container. Reset `xhost` after you are done with using the MIRACL GUI using:

```
xhost -
```

The above will enable/disable access for all users. If this is not the desired behavior, access can be granted in a more [fine grained manner](https://www.x.org/archive/X11R6.8.1/doc/xhost.1.html).

Example:

```
xhost +SI:localsuer:<yourusername>
```

(replace `<yourusername>` with the actual user name of your host system)

### Q: I cannot run X or Y with Docker because of permission denied errors:

If you have not set up a Docker user you might need to run Docker commands with `sudo`.

### Q: Processes that require TrackVis or Diffusion Toolkit are not working:

Because of their respective licenses, we could not include TackVis or Diffusion Toolkit in our Docker image directly.
Please download and install them on you host machine using their [installation guide](http://trackvis.org/docs/?subsect=installation).
After they have been successfully installed, mount a volume to your MIRACL Docker container that contains the binary folder for TackVis and Diffusion Toolkit.
The last step is to add the binaries to your `$PATH` within your MIRACL Docker container.

### Q: I need to install or make changes to apps in the MIRACL container but my user is not authorized to do so:

The user in the container is the user of your host machine. This is done to avoid issues with the MIRACL GUI and X11. If you need to make changes that require sudo privileges, just log out of your container and log back in as root:

```
$ docker exec -it -u root miracl bash
```

After making your changes, log out and log back in with your regular user:

```
$ docker exec -it miracl bash
```

### Q: I do not want to create the image using the provided script:

You can build the image yourself, not using the script we provide. However, the build script makes sure that the GUI version of MIRACL works with Docker and it is therefore recommended to use it.
Build the image with:

```
$ docker build -t mgoubran/miracl .
```

(notice the . at the end)

To run the container use:

```
$ docker run -it mgoubran/miracl bash
```

All changes will be lost when you shell out. The MIRACL GUI will be unlikely to work but you can try the troubleshooting steps in the following section to make it work.

### Q: I get either or both of the following errors whenever I try to run the GUI from within a Docker container that was build without the provided build script:

```
Authorization required, but no authorization protocol specified
qt.qpa.xcb: could not connect to display :1
```

(The number for the display could be different in your case)

```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.
```

Exit your running Docker container and run the following
to mount an X11 socket from the host system in a new Docker container:

```
docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mgoubran/miracl bash
```

If you still receive the above error, you may have to change your `xhost` access control ([see previous troubleshooting step](#q-the-gui-miraclgui-is-not-working)).

## Singluarity

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

Because of their respective licenses, we could not include TackVis or Diffusion Toolkit in our Singularity container directly.
Please download and install them on you host machine using their [installation guide](http://trackvis.org/docs/?subsect=installation).
After they have been successfully installed, mount a volume to your MIRACL Singularity container that contains the binary folder for TackVis and Diffusion Toolkit.
The last step is to add the binaries to your `$PATH` within your MIRACL Singularity container.

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

## Local install

### Q: I get the following error whenever I try to run the GUI: qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "{anaconda path}/envs/miracl_merge/lib/python3.7/site-packages/cv2/qt/plugins" even though it was found.

If you know the path to the environment name, try running the following line to remove the specific file in question:

    rm "{path_to_environment_name}/lib/python3.7/site-packages/cv2/qt/plugins/platforms/libqxcb.so"
