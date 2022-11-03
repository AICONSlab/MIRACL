# Docker Install

Docker is well suited if you want to run it on a local machine or local server. If you need to run MIRACL on a cluster,
see the [Singularity install](install-singularity.md). If you don't have Docker installed on
your computer, [do that first](https://docs.docker.com/engine/installation/). Make sure your installation includes Docker Compose as it is needed to run the build script we provide.
Docker Compose is included as part of the Docker Desktop installation by default.

## Getting Started

First, it is important to understand how the container is built. There is a base image
in the [docker](../docker) folder that installs Python and dependencies.
Then the [Dockerfile](../Dockerfile) in the base of the repository builds
the [mgoubran/miracl](https://hub.docker.com/r/mgoubran/miracl) image from
that base. When the build happens, it cats the [version.txt](../miracl/version.txt)
file in the repository to save a versioned base, but then the build
uses the tag `base-latest` that is always the latest base.
The base container is built from this folder and pushed manually, while the
main container is built and pushed automatically via the [CircleCI Recipe](../.circleci/config.yml).
Thus, if you want to update the base, you will need to [see the README.md](../docker)
in that folder and push new images.

## Build from scratch

Clone the MIRACL repo to your machine:

```
$ git clone https://www.github.com/mgoubran/MIRACL
$ cd MIRACL
```

Build the image using the build script we provide:

```
$ ./build.sh
```

(make sure that the script can be executed. If it can't and you are the owner of the file, use `chmod u+x build.sh` to make it executable. Prefix with `sudo` if you are not the owner of the file.)

Once the image has successfully been built, run the container using Docker Compose:

```
$ docker-compose up -d
```

The container is now running and ready to be used.
  
## Using the container

Interactively shell inside:

```
$ docker exec -it miracl bash
```

Files that are saved while using MIRACL should be saved to volumes mounted into the container in order to make them persistent. To mount volumes, just add them to the `docker-compose.yml` in the base directory under `volumes` (do not delete the volume that is already mounted which mounts your `.Xauthority`).

Example:

```
volumes:
      - /home/mgoubran/.Xauthority:/home/mgoubran/.Xauthority
      - /home/mgoubran/mydata:/home/mgoubran/mydata
```

## Stopping the container

Exit your container and navigate to your MIRACL folder. Use Docker Compose to stop the container:

```
$ docker-compose down
```

## Troubleshooting

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

### Q: I get either or both of the following errors whenever I try to run the GUI from within a Docker container that I built not using the build script:

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

If this happened without using the build script i.e. you build the image yourself, exit your running Docker container and run the following
to mount an X11 socket from the host system in a new Docker container:

```
docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mgoubran/miracl bash
```

If you still receive the above error, you may have to change your `xhost` access control ([see previous troubleshooting step](#q-the-gui-miraclgui-is-not-working)).
