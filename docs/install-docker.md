# Docker Install

Docker is well suited if you want to run it locally. If you need to run on a cluster,
see the [Singularity install](install-singularity.md). If you don't have Docker installed on
your computer, [do that first](https://docs.docker.com/engine/installation/).

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

The image comes with the following:

 - system Python, version 2.7.6, and pip
 - 

  
### Using the image

Interactively shell inside

```
docker run -it mgoubran/miracl bash
```

(this will be lost when you shell out)
