# Docker Install

Docker is well suited if you want to run it on a local machine or local server.
If you need to run MIRACL on a cluster, see our instructions for
[installing Singularity](install-singularity.md). If you don't have Docker 
installed on your computer, 
[do that first](https://docs.docker.com/engine/installation/). Make sure your 
installation includes [Docker Compose](https://docs.docker.com/compose/install/)
as it is needed to run the build script we provide. Note that Docker Compose 
is included as part of the Docker Desktop installation by default.

## Getting Started

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
$ docker compose up -d
```

(note that the Docker Compose syntax is different if you installed it using the standalone method. Compose standalone uses the `-compose` syntax instead of the current standard syntax `compose`. The above command would thus be `docker-compose up -d` when using Compose standalone.)

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
$ docker compose down
```

(note that the Docker Compose syntax is different if you installed it using the standalone method. Compose standalone uses the `-compose` syntax instead of the current standard syntax `compose`. The above command would thus be `docker-compose up -d` when using Compose standalone.)

## Troubleshooting

Please refer to our [Troubleshooting](troubleshooting.md) section.
