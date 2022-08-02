# Docker Install

Docker is well suited if you want to run it locally. If you need to run on a cluster,
see the [Singularity install](install-singularity.md). If you don't have Docker installed on
your computer, [do that first](https://docs.docker.com/engine/installation/).

## Getting Started

First, you should understand how the container is built. There is a base image
in the [docker](../docker) folder that installs Python and dependencies,
and then the [Dockerfile](../Dockerfile) in the base of the repository builds
the [mgoubran/miracl](https://hub.docker.com/r/mgoubran/miracl) image from
that base. When the build happens, it cats the [version.txt](../miracl/version.txt)
file in the repository in the repo to save a versioned base, but then the build
uses the tag `base-latest` that is always the latest base.
The base container is built from this folder and pushed manually, while the
main container is built and pushed automatically via the [CircleCI Recipe](../.circleci/config.yml).
Thus, if you want to update the base, you will need to [see the README.md](../docker)
in that folder and push new images.

## Build from scratch

```
git clone https://www.github.com/mgoubran/MIRACL
cd MIRACL
```
Build the image using the Dockerfile

```
docker build -t mgoubran/miracl .
```

(notice the `.` at the end)

  
### Using the image

Interactively shell inside

```
docker run -it mgoubran/miracl bash
```

(this will be lost when you shell out)

## Troubleshooting

### Q: I get either or both of the following errors whenever I try to run the GUI from within the Docker container:

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

Exit your running Docker container and run the following to mount an X11 socket from the host system in a new Docker container:

```
docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mgoubran/miracl bash
```

If you still receive the above error, you may have to change your `xhost` access control on your host machine (**not** within your Docker container). Exit the running Docker container and type:

```
xhost +
```

This will disable access control for `xhost`. Start a new Docker container with the above command.

Once you are done with working in the container, exit it and enable access control again on the host machine:

```
xhost -
```
