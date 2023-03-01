# Installing and running MIRACL

We provide instructions on how to install and run MIRACL using either of the 
following methods:

- **[Docker](#docker-installation)**: Install and run MIRACL using Docker. We provide a build script to automatically 
create a Docker image for you that can be run using Docker Compose. This method 
does not require a manual installation of MIRACL and works on Linux, macOS 
and Windows (using [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/)).

> This is our recommended method for running MIRACL on local machines and servers.

- **[Singularity](#singularity-installation)**: Run MIRACL inside a Singularity container that is well suited for SLURM cluster 
environments such as Compute Canada or Sherlock at Stanford. We provide a 
compiled Singularity container that can be downloaded directly and does not 
require manually installing MIRACL. Singularity runs natively on Linux and can 
be used on macOS or Windows using virtual machines.

> This is our recommended method for running MIRACL on SLURM clusters.

- **[Local](#local-installation)**: A series of manual commands that will allow you to install and run MIRACL on 
your local Linux or macOS machine. This method requires you to set up MIRACL 
manually and install and set up all of its dependencies.

> We do not recommend this method.

- **[Windows](#windows-installation)**: Install and run MIRACL on Windows using 
[WSL 2](https://learn.microsoft.com/en-us/windows/wsl/). MIRACL will have to 
be installed in WSL 2 locally using the local install instructions.

> We do not recommend this method.

---

## Docker installation

Docker is well suited if you want to run MIRACL on a local machine or local server.
If you need to run MIRACL on a cluster, see our instructions for
[installing Singularity](install-singularity.md). If you don't have Docker 
installed on your computer, 
[do that first](https://docs.docker.com/engine/installation/). Make sure your 
installation includes [Docker Compose](https://docs.docker.com/compose/install/)
as it is needed to run the build script we provide. Note that Docker Compose 
is included as part of the Docker Desktop installation by default.

### Getting started

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

### Build MIRACL from scratch

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
  
### Using the container

Interactively shell inside:

```
$ docker exec -it miracl bash
```

Files that are saved while using MIRACL should be saved to volumes mounted
into the container in order to make them persistent. To mount volumes, just
add them to the `docker-compose.yml` in the base directory under `volumes`.

> Do not delete the volume that is already mounted which mounts your `.Xauthority`!

Example:

```
volumes:
      - /home/mgoubran/.Xauthority:/home/mgoubran/.Xauthority
      - /home/mgoubran/mydata:/home/mgoubran/mydata
```

### Stopping the container

Exit your container and navigate to your MIRACL folder. Use Docker Compose to stop the container:

```
$ docker compose down
```

> Note that the Docker Compose syntax is different if you installed it using
the standalone method. Compose standalone uses the `-compose` syntax instead of
the current standard syntax `compose`. The above command would thus be
`docker-compose up -d` when using Compose standalone.

### Additional build options

#### Image and container naming

Naming is done automatically when using our build script which includes a 
default naming scheme. By default, the image is named `mgoubran/miracl:latest`
and the container is tagged with `miracl`.

You can easily change the defaults if your usecase requires it by running our 
build script with the following options:

```
$ ./build -i <image_name> -c <container_name>
```

Options:

```
-i, Specify image name (default: mgroubran/miracl)
-c, Specify container name (default: miracl)
```

Example:

```
$ ./build -i josmann/miracl -c miracl_dev_version
```

> Use `./build -h` to show additional options.

#### MIRACL versions

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

4. If you are reverting to a version of MIRACL >= `2.2.4`, you can build the 
image for your chosen version by running the build script with the `-t` flag:

```
$ ./build.sh -s
```

> If you want to build an image for a version of MIRACL <= `2.2.4` either 
follow the build instructions of the particular version or download the latest 
build script using e.g. 
`wget https://raw.githubusercontent.com/AICONSlab/MIRACL/master/build.sh` 
(overwrites current build script if present) and run it with the `-t` flag.

5. From here you can follow our instructions for 
[building MIRACL from scratch](#build-miracl-from-scratch) starting with 
`docker compose up -d`. Our script will automatically detect the 
version of the branch you checked out and tag the image accordingly.

---

## Singularity installation

Unlike Docker, Singularity is well suited to run in a cluster environment
(like Sherlock at Stanford or Compute Canada). We provide the latest version 
of MIRACL as a Singularity container that can be conveniently pulled from cloud 
storage.

### Download container

First, log in to the cluster:

```
$ ssh -Y username@cluster
```

`cluster` could be "sherlock.stanford.edu" or "cedar.computecanada.ca" 
for example.

Once logged in, change the directory to your scratch space and pull (download) 
the Singularity container:

```
$ cd $SCRATCH
$ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest
```

> `singularity pull` requires Singularity version `3.0.0` or higher. Please refer
to our [Troubleshooting](./troubleshooting.md) section ("Q: Can I build a 
Singularity container from the latest MIRACL image on Docker Hub") if you are
using an older version of Singularity.

### Interaction

To shell into the container use:

```
$ singularity shell miracl_latest.sif bash
```

Use the `-B` flag to bind a data directory to the container:

```
$ singularity shell -B /data:/data miracl_latest.sif bash
```

> For running functions on clusters please check our Singularity tutorials for
[Compute Canada](./tutorials/compute_canada/compute_canada.md) and
[Sherlock](./tutorials/sherlock/sherlock.md)

---

## Local installation

Steps to setup/run MIRACL on a Linux/macOS machine:

```
$ git clone https://github.com/mgoubran/MIRACL.git miracl
```

(or download the zip file containg the repo and uncompress it), then:

```
$ cd miracl
```

To setup a virtual environment, download Anaconda for Python 2.7:
https://www.anaconda.com/distribution/#download-section,

Then create the environment:

```
$ conda create --name miracl python=3.7.4 pip
$ conda activate miracl
```

Install dependencies:

```
$ pip install -e .
```

### ANTS & c3d

Place the `depends` folder inside `linux_depends` or `mac_depends` (based on your OS), found here:

[download link](https://www.dropbox.com/sh/i9swdedx7bsz1s8/AABpDmmN1uqPz6qpBLYLtt8va?dl=0)

Inside the `miracl` folder do:

```
$ mv ~/Downloads/depends.zip miracl/.
$ cd miracl
$ unzip depends.zip
$ rm depends.zip
```

This folder contains compiled versions of **ANTS** and **c3d** for Linux or Mac OS. Before continuing, make sure to change the permissions. This can be done by running

```
$ chmod -R 755 <path/to/depends>/*
```

In order to run the pipeline, some symbolic links must be added to access certain commands. Inside the **miracl** folder, run:

```
$ sudo ln -s <path/to/depends>/ants/antsRegistrationMIRACL.sh /usr/bin/ants_miracl_clar && chmod +x /usr/bin/ants_miracl_clar
$ sudo ln -s <path/to/depends>/ants/antsRegistrationMIRACL_MRI.sh /usr/bin/ants_miracl_mr && chmod +x /usr/bin/ants_miracl_mr
```

Make sure `<path/to/depends>` is replaced with the directory path that leads to the depends directory.

### Allen atlases

Place the `atlases` folder in the same link above inside the `miracl` folder:

```
$ mv ~/Downloads/atlases.zip miracl/.
$ cd miracl
$ unzip atlases.zip
$ rm atlases.zip
```

This folder contains the Allen atlas data needed for registration and connectivity analysis.

### Fiji & FSL

Install Fiji & FSL:

[Fiji/ImageJ](https://imagej.net/Fiji/Downloads)

For Linux:

```
$ cd depends
$ wget https://downloads.imagej.net/fiji/latest/fiji-linux64.zip
$ unzip fiji-linux64.zip
$ rm fiji-linux64.zip
```

Install additional plugins:

Go to Help -> Update and press "Manage update sites" button.

Choose the following update sites there:

```
$ 3D ImageJ Suite: http://sites.imagej.net/Tboudier
$ Biomedgroup: https://sites.imagej.net/Biomedgroup
$ IJPB-plugins: http://sites.imagej.net/IJPB-plugins
```

[FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

```
$ wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
$ sudo python fslinstaller.py
```

### Visualization

For the visualization of nifti files and labels we recommend [ITKSNAP](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3)

or the [nifti plugin](https://imagej.nih.gov/ij/plugins/nifti.html) for Fiji/ImageJ

### Diffusion Data

If you have diffusion MRI data install:

[MRtrix3](http://www.mrtrix.org)

```
$ sudo apt-get install git g++ python python-numpy libeigen3-dev zlib1g-dev libqt4-opengl-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev
$ git clone https://github.com/MRtrix3/mrtrix3.git
$ cd mrtrix3
$ ./configure
$ ./build
$ ./set_path
```

### Deactivate

To end session

```
$ conda deactivate
```

### Update MIRACL

To update MIRACL, run

```
$ cd miracl
$ git pull
```

You should be good to go!

---

## Windows installation

To install MIRACL on your Windows system, Windows Subsystem for Linux (WSL) 
must be installed. WSL2 is 
[preferred](https://docs.microsoft.com/en-us/windows/wsl/compare-versions). 
From there, the usual steps to install MIRACL on a Linux based system will be 
used, with a few tweaks.

> Follow the below steps if you want to install MIRACL in the your WSL 
instance locally. If you prefer to use Docker to run MIRACL on Windows follow 
our [installation instructions for Docker](install-docker.md) instead.

### Installing WSL 2 on Windows

The Windows Subsystem for Linux (WSL) creates an environment that allows users 
to run versions of Linux without having to set up a virtual machine or 
different computer. One of the long term benefits of WSL is the ability for 
students, developers, and researchers to run other command tools, and to run 
Bash shell scripts.

To install WSL, users can follow the instructions in the 
[following link from Microsoft](https://docs.microsoft.com/en-us/windows/wsl/install). 
More comprehensive instructions can be found 
[here](https://www.windowscentral.com/install-windows-subsystem-linux-windows-10). 
Upgrading from WSL 1 to WSL 2 is recommended, due to 
[WSL 2's benefits](https://docs.microsoft.com/en-us/windows/wsl/compare-versions).

### Install the Ubuntu distribution (Ubuntu 22.04) from the Microsoft Store

If users either have a preferred Linux distribution, this step may be ignored.

A Linux distribution (distro) is an operating system based on the Linux kernel.

Now that WSL (either 1 or 2) is installed, the Ubuntu 22.04 distro can be 
installed. To install Ubuntu, open the Windows Store app, search for 
"Ubuntu 22.04", and select the "Get" button. The following 
[link](https://www.microsoft.com/en-gb/p/ubuntu-2004-lts/9n6svws3rx71) can also 
be used.

### Install Python and pip

The Ubuntu distro should have Python 3 installed. To ensure that this is the 
case, update all packages installed in the WSL:

```
$ sudo apt update
$ sudo apt -y upgrade
```

We can see which version of Python 3 is installed by typing:

```
$ python3 -V
```

The output in the terminal window will show the version number.

`pip` is now required to install software packages in Python. It can be 
installed by running the following command:

```
$ sudo apt install -y python3-pip
```

Anaconda can also be installed, but we found that installing and using `pip` 
was more straightforward.

### Install MIRACL using local installation instructions

To install MIRACL, the local installation instructions can be followed 
[here](./install-local.md).

### Installing Xming

To use MIRACL's graphical user interface (GUI), Xming must be installed. Xming 
is a display server for Windows computers, that is available for use by anyone. 
It can be downloaded 
[here](https://www.google.com/url?q=https://sourceforge.net/projects/xming/&source=gmail&ust=1641769602186000&usg=AOvVaw2MoTURhTsyCk_-56M3Qljj).

Before running MIRACL's GUI, run Xming. In the terminal window where MIRACL's 
GUI will be run, input the following command:

```
$ export DISPLAY=$DISPLAY:localhost:0
```

### Running MIRACL with WSL 2

Now that everything is installed, MIRACL can be run via WSL. To run:

1. Open WSL via terminal
2. Navigate to the folder where you would like to run MIRACL from
3. Activate the environment containing `miracl`

```
$ source activate miracl
$ miraclGUI
```

---

## Troubleshooting

Please refer to our [Troubleshooting](../troubleshooting.md) section.
