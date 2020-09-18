# Docker Base Image

This folder provides the recipe and instructions for building the base image
to support `mgoubran/miracl`. The dependencies take quite some time to install,
and so this base speeds things up by providing them most in the base.
Since this image is unexpected to change, the maintainer has built it locally
and then will push manally. Instructions are provided here to reproduce this.

## Build the base

To build the base container, first understand the naming convention. We name
the container base based on the version of the software.

```bash
VERSION=$(cat ../miracl/version.txt)
$ echo $VERSION 
1.1.0
```

Next, build the base container. We will give it tag "base-latest" and the version tag
will be applied after:

```bash
$ docker build -t mgoubran/miracl:base-latest .
```

Next, tag the container with the version:

```bash
$ docker tag mgoubran/miracl:base-latest mgoubran/miracl:base-$VERSION 
```

## Push to Docker Hub

And then push both to Docker Hub

```bash
$ docker push mgoubran/miracl:base-latest
$ docker push mgoubran/miracl:base-$VERSION
```

Next, when the continuous integration builds the image, it will also cat the
version.txt file, and use the correct version as the base.
