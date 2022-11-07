# Installing on Windows

To install MIRACL on your Windows system, Windows Subsystem for Linux (WSL) must be installed. WSL2 is [preferred](https://docs.microsoft.com/en-us/windows/wsl/compare-versions). From there, the usual steps to install MIRACL on a Linux based system will be used, with a few tweaks.

> Follow the below steps if you want to install MIRACL in the your WSL instance locally. If you prefer to use Docker to run MIRACL on Windows follow our [installation instructions for Docker](install-docker.md) instead.

## Installing WSL 2 on Windows
The Windows Subsystem for Linux (WSL) creates an environment that allows users to run versions of Linux without having to set up a virtual machine or different computer. One of the long term benefits of WSL is the ability for students, developers, and researchers to run other command tools, and to run Bash shell scripts.

To install WSL, users can follow the instructions in the [following link from Microsoft](https://docs.microsoft.com/en-us/windows/wsl/install). More comprehensive instructions can be found [here](https://www.windowscentral.com/install-windows-subsystem-linux-windows-10). Upgrading from WSL 1 to WSL 2 is recommended, due to [WSL 2's benefits](https://docs.microsoft.com/en-us/windows/wsl/compare-versions).

## Install the Ubuntu distribution (Ubuntu 22.04) from the Microsoft Store
If users either have a preferred Linux distribution, this step may be ignored.

A Linux distribution (distro) is an operating system based on the Linux kernel.

Now that WSL (either 1 or 2) is installed, the Ubuntu 22.04 distro can be installed. To install Ubuntu, open the Windows Store app, search for "Ubuntu 22.04", and select the "Get" button. The following [link](https://www.microsoft.com/en-gb/p/ubuntu-2004-lts/9n6svws3rx71) can also be used.

## Install Python and pip

The Ubuntu distro should have Python 3 installed. To ensure that this is the case, update all packages installed on WSL

    sudo apt update
    sudo apt -y upgrade

We can see which version of Python 3 is installed by typing:

    python3 -V

The output in the terminal window will show the version number.

`pip` is now required to install software packages in Python. It can be installed by running the following command:

    sudo apt install -y python3-pip

Anaconda can also be installed, but we found that installing and using `pip` was more straightforward.

## Install MIRACL using local installation instructions

To install MIRACL, the local installation instructions can be followed [here](install-local.md).

## Installing Xming

To use MIRACL's graphical user interface (GUI), Xming must be installed. Xming is a display server for Windows computers, that is available for use by anyone. It can be downloaded [here](https://www.google.com/url?q=https://sourceforge.net/projects/xming/&source=gmail&ust=1641769602186000&usg=AOvVaw2MoTURhTsyCk_-56M3Qljj).

Before running MIRACL's GUI, run Xming. In the terminal window where MIRACL's GUI will be run, input the following command

    export DISPLAY=$DISPLAY:localhost:0

## Running MIRACL with WSL 2

Now that everything is installed, MIRACL can be run via WSL. To run,

1. Open WSL via terminal
2. Navigate to the folder where you would like to run MIRACL from
3. Activate the environment containing `miracl`

```
source activate miracl
miraclGUI
```

## Troubleshooting

Please refer to our [Troubleshooting](troubleshooting.md) section.
