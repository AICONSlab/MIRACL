# Docker Install

Docker is well suited if you want to run it locally. If you need to run on a cluster,
see the [Singularity install](install-singularity.md). If you don't have Docker installed on
your computer, [do that first](https://docs.docker.com/engine/installation/).

## Getting Started

First, you should understand how the container is built. There is a base image
in the [docker](../docker) folder that installs Python and dependencies,
and then the [Dockerfile](../Dockerfile) in the base of the repository builds
the [mgoubran/miracl](https://hub.docker.com/r/mgoubran/miracl) image from
that base. When the build happens, it cats the [version.txt](../version.txt)
file in the repository in the repo to save a versioned base, but then the build
uses the tag `base-latest` that is always the latest base.
The base container is built from this folder and pushed manually, while the
main container is built and pushed automatically via the [CircleCI Recipe](../.circleci/config.yml).
Thus, if you want to update the base, you will need to [see the README.md](../docker)
in that folder and push new images.

## Build from scratch

```
git clone https://www.github.com/mgoubran/MIRACLdev
cd MIRACLdev
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
