# Installing and running MIRACL

We provide instructions on how to install and run MIRACL using either of the following three methods:

- [Docker install](install-docker.md): Install and run MIRACL using Docker. We provide a build script to
automatically create a Docker image for you that can be run using Docker-Compose. This method does not
require a manual installation of MIRACL and works on Linux, Mac OS X and Windows
(using [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/)). **This is our recommended method for
running MIRACL on local machines and servers.**

- [Singularity install](install-singularity.md): Run MIRACL inside a Singularity container. We provide a
compiled Singularity container that can be downloaded directly and does not require manual installing MIRACL.
Singularity runs natively on Linux and can be used on Mac OS X or Windows using virtual machines. **This is
our recommended method for running MIRACL on SLURM clusters.** 

- [Local install](install-local.md): A series of manual commands that will allow you to install and run
MIRACL on your local Linux or Mac OS X machine. This method requires you to set up MIRACL manually and
install and set up all of its dependencies. **We do not recommend this method.**

- [Windows install](install-windows.md): Install and run MIRACL on Windows using
[WSL 2](https://learn.microsoft.com/en-us/windows/wsl/). MIRACL will have to be installed in WSL 2 locally
using the local install instructions. **We do not recommend this method.**
