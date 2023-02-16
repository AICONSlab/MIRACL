# Docker installation

Docker is well suited if you want to run it on a local machine or local server.
If you need to run MIRACL on a cluster, see our instructions for
[installing Singularity](install-singularity.md). If you don't have Docker 
installed on your computer, 
[do that first](https://docs.docker.com/engine/installation/). Make sure your 
installation includes [Docker Compose](https://docs.docker.com/compose/install/)
as it is needed to run the build script we provide. Note that Docker Compose 
is included as part of the Docker Desktop installation by default.

## Getting started

First, it is important to understand how the container is built. There is a 
base image in the [docker](../docker) folder that installs Python and 
dependencies. Then the [Dockerfile](../Dockerfile) in the base of the
repository builds the [mgoubran/miracl](https://hub.docker.com/r/mgoubran/miracl)
image from that base. When the build happens, it cats the [version.txt](../miracl/version.txt)
file in the repository to save a versioned base, but then the build uses the
tag `revised-base-latest` that is always the latest base. The base container is
built from this folder and pushed manually, while the main container is built
and pushed automatically via the [CircleCI Recipe](../.circleci/config.yml).
Thus, if you want to update the base, you will need to [see the README.md](../docker)
in that folder and push new images.

## Build MIRACL from scratch

> This will build a Docker image of MIRACL based on its latest version using 
our default naming scheme. For custom names and specific versions see our 
[Additional build options section](#additional-build-options)

Clone the MIRACL repo to your machine:

```
$ git clone https://www.github.com/mgoubran/MIRACL
$ cd MIRACL
```

Build the latest MIRACL image using the build script we provide:

```
$ ./build.sh
```

> Make sure that the script can be executed. If it can't and you are the owner
of the file, use `chmod u+x build.sh` to make it executable. Prefix with `sudo`
if you are not the owner of the file or change permissions for `g` and/or `o`.

Once the image has successfully been built, run the container using Docker Compose:

```
$ docker compose up -d
```

> Note that the Docker Compose syntax is different if you installed it using
the standalone method. Compose standalone uses the `-compose` syntax instead of
the current standard syntax `compose`. The above command would thus be
`docker-compose up -d` when using Compose standalone.

The container is now running and ready to be used.
  
## Using the container

Interactively shell inside:

```
$ docker exec -it miracl bash
```

Files that are saved while using MIRACL should be saved to volumes mounted
into the container in order to make them persistent. To mount volumes, just
add them to the `docker-compose.yml` in the base directory under `volumes`
(do not delete the volume that is already mounted which mounts your `.Xauthority`).

Example:

```
volumes:
      - /home/mgoubran/.Xauthority:/home/mgoubran/.Xauthority
      - /home/mgoubran/mydata:/home/mgoubran/mydata
```

## Stopping the container

Exit your container and navigate to your MIRACL folder. Use Docker Compose to stop the container:

```
$ docker compose down
```

> Note that the Docker Compose syntax is different if you installed it using
the standalone method. Compose standalone uses the `-compose` syntax instead of
the current standard syntax `compose`. The above command would thus be
`docker-compose up -d` when using Compose standalone.

## Additional build options

### Image and container naming

Naming is done automatically when using our build script which includes a 
default naming scheme. By default, the image is named `mgoubran/miracl:latest`
and the container is tagged with `miracl`.

You can easily change the defaults if your usecase requires it by running our 
build script with the following options:

```
$ ./build -i <image_name> -c <container_name>
```

-  *-i*, Specify image name (default: mgroubran/miracl)
-  *-c*, Specify container name (default: miracl)

Example:

```
$ ./build -i josmann/miracl -c miracl_dev_version
```

> Use `./build -h` to show additional options.

## MIRACL versions

By default, Docker images will be built using the latest version of MIRACL. 
If you need to build a Docker image based on a specific version of MIRACL, 
do the following:

1. Clone the MIRACL repository and navigate to the MIRACL folder:

```
$ git clone https://www.github.com/mgoubran/MIRACL
$ cd MIRACL
```

2. Cloning the repository will download all tags/versions. List them with:

```
$ git tag -l
```

Example output:

```
v1.1.1
v2.2.1
v2.2.2
v2.2.3
```

3. Decide which tag/version of MIRACL you want to use and check it out as a 
new branch:

```
$ git checkout tags/<tag_name> -b <branch_name>
```

Example:

```
$ git checkout tags/v2.2.1 -b miracl_v2.2.1
```

4. From here you can follow our instructions for 
[building MIRACL from scratch](#build-miracl-from-scratch) starting with 
running the build script we provide. Our script will automatically detect the 
version of the branch you checked out and tag the image accordingly.

## Troubleshooting

Please refer to our [Troubleshooting](troubleshooting.md) section.
