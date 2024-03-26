Installing and running MIRACL
#############################

We provide instructions on how to install and run :program:`MIRACL` using 
either of the following methods:

.. important::
   :program:`Docker` is our recommended method for running :program:`MIRACL` 
   on local machines and servers. We recommend :program:`Singularity` to run 
   :program:`MIRACL` in a cluster environment (e.g. Compute Canada).

.. attention::
   Support for installing :program:`MIRACL` locally (i.e. on your host 
   system directly without using :program:`Docker` or :program:`Singularity`) 
   will be phased out in future versions of the software

.. tabs::

   .. tab:: Docker

      We provide a build script to automatically create a :program:`Docker` 
      image for you that can be run using :program:`Docker Compose`. This 
      method does not require a manual installation of :program:`MIRACL` and 
      works on Linux, macOS and Windows (using WSL 2).

      .. tip::
         This is our recommended method for running :program:`MIRACL` on local 
         machines and servers

      Docker is well suited if you want to run :program:`MIRACL` on a local 
      machine or local server. If you need to run :program:`MIRACL` on a 
      cluster, see our instructions for installing :program:`Singularity`. If 
      you don't have Docker installed on your computer, do that first. Make 
      sure your installation includes :program:`Docker Compose` as it is 
      required to run the build script we provide. Note that :program:`Docker 
      Compose` is included as part of the :program:`Docker Desktop` 
      installation by default.

      .. raw:: html

         <h2>Getting started</h2>

      First, it is important to understand how the container is built. There 
      is a base image in the docker folder that installs :program:`Python` and 
      dependencies. Then the ``Dockerfile`` in the base of the repository 
      builds the ``mgoubran/miracl`` image from that base. When the build 
      happens, it cats the ``version.txt`` file in the repository to save a 
      versioned base, but then the build uses the tag revised-base-latest that 
      is always the latest base. The base container is built from this folder 
      and pushed manually, while the main container is built and pushed 
      automatically via the :program:`CircleCI` Recipe. Thus, if you want to 
      update the base, you will need to see the ``README.md`` in that folder 
      and push new images.

      .. raw:: html

         <h2>Build MIRACL from scratch</h2>

      This will build a :program:`Docker` image of :program:`MIRACL` based on 
      its latest version using our default naming scheme. For custom names and 
      specific versions see below for our ``Additional build options`` section.

      Clone the :program:`MIRACL` repo to your machine:

      .. code-block::

         $ git clone https://www.github.com/mgoubran/MIRACL
         $ cd MIRACL

      Build the latest :program:`MIRACL` image using the build script we 
      provide:

      .. code-block::

         $ ./build.sh

      .. error::
         Make sure that the script can be executed. If it can't and you are 
         the owner of the file, use ``chmod u+x build.sh`` to make it 
         executable. Prefix with ``sudo`` if you are not the owner of the file 
         or change permissions for ``g`` and/or ``o``.

      Once the image has successfully been built, run the container using 
      :program:`Docker Compose`:

      .. code-block::

         $ docker compose up -d

      .. include:: ../directives/docker_compose_directive.rst

      The container is now running and ready to be used.

      .. raw:: html

         <h2>Using the container</h2>
      
      Interactively shell inside:
      
      .. code-block::

         $ docker exec -it miracl bash
      
      Files that are saved while using :program:`MIRACL` should be saved to 
      volumes mounted into the container in order to make them persistent. To 
      mount volumes, just add them to the ``docker-compose.yml`` in the base 
      directory under volumes.
      
      .. danger::
         Do not delete the volume that is already mounted which mounts 
         your ``.Xauthority``! This is important for X11 to work correctly.
      
      Example:
      
      .. code-block::

         volumes:
               - '/home/mgoubran/.Xauthority:/home/mgoubran/.Xauthority'
               - '/home/mgoubran/mydata:/home/mgoubran/mydata'

      .. raw:: html

         <h2>Stopping the container</h2>
      
      Exit your container and navigate to your :program:`MIRACL` folder. Use 
      :program:`Docker Compose` to stop the container:
      
      .. code-block::

         $ docker compose down
      
      .. include:: ../directives/docker_compose_directive.rst

      .. raw:: html

         <h2>Additional build options</h2>

      .. raw:: html

         <h3>Image and container naming</h3>
      
      Naming is done automatically when using our build script which includes 
      a default naming scheme. By default, the image is named 
      ``mgoubran/miracl:latest`` and the container is tagged with ``miracl``.
      
      You can easily change the defaults if your usecase requires it by 
      running our build script with the following options:
      
      .. code-block::

         $ ./build -i <image_name> -c <container_name>
      
      Options:
      
      .. code-block::

         -i, Specify image name (default: mgroubran/miracl)
         -c, Specify container name (default: miracl)
      
      Example:
      
      .. code-block::

         $ ./build -i josmann/miracl -c miracl_dev_version
      
      .. tip::
         Use ``./build -h`` to show additional options
      
      .. raw:: html

         <h2>MIRACL versions</h2>
      
      By default, :program:`Docker` images will be built using the latest 
      version of :program:`MIRACL`. If you need to build a :program:`Docker` 
      image based on a specific version of :program:`MIRACL`, do the following:
      
      1. Clone the :program:`MIRACL` repository and navigate to the 
         :program:`MIRACL` folder:
      
      .. code-block::

         $ git clone https://www.github.com/mgoubran/MIRACL
         $ cd MIRACL
      
      2. Cloning the repository will download all tags/versions. List them with:
      
      .. code-block::

         $ git tag -l
      
      Example output:
      
      .. code-block::

         v1.1.1
         v2.2.1
         v2.2.2
         v2.2.3
         v2.2.4
         v2.2.5
      
      3. Decide which tag/version of :program:`MIRACL` you want to use and 
         check it out as a new branch:
      
      .. code-block::

         $ git checkout tags/<tag_name> -b <branch_name>
      
      Example:
      
      .. code-block::

         $ git checkout tags/v2.2.4 -b miracl_v2.2.4
      
      4. If you are reverting to a version of MIRACL >= ``2.2.4``, you can 
         build the image for your chosen version by running the build script 
         with the ``-t`` flag:
      
      .. code-block::

         $ ./build.sh -t
      
      .. note::
         If you want to build an image for a version of MIRACL <= ``2.2.4`` 
         either follow the build instructions of the particular version or 
         download the latest build script using e.g. ``wget https://raw.githubusercontent.com/AICONSlab/MIRACL/master/build.sh``
         (overwrites current build script if present) and run it with the 
         ``-t`` flag.
      
      5. From here you can follow our instructions for building 
         :program:`MIRACL` from scratch starting with ``docker compose up -d``. 
         Our script will automatically detect the version of the branch you 
         checked out and tag the image accordingly.

   .. tab:: Singularity

      Unlike :program:`Docker`, :program:`Singularity` is well suited to run in 
      a cluster environment (like Sherlock at Stanford or Compute Canada). We 
      provide the latest version of :program:`MIRACL` as a 
      :program:`Singularity` container that can be conveniently pulled from 
      cloud storage.

      .. tip::
         This is our recommended method for running :program:`MIRACL` in a 
         SLURM cluster environment such as Compute Canada or Sherlock @ 
         Stanford

      .. raw:: html

         <h2>Download container</h2>

      First, log in to the cluster:
      
      .. code-block::

         $ ssh -Y <username>@<cluster>
      
      ``<cluster>`` could be ``sherlock.stanford.edu`` or 
      ``cedar.computecanada.ca`` for example
      
      Once logged in, change the directory to your scratch space and pull 
      (download) the :program:`Singularity` container:
      
      .. code-block::

         $ cd $SCRATCH
         $ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest
      
      .. attention::
         ``singularity pull`` requires :program:`Singularity` version ``3.0.0`` 
         or higher. Please refer to our 
         :doc:`Troubleshooting section <../troubleshooting/troubleshooting_singularity>`
         ("Can I build a Singularity container from the latest MIRACL 
         image on Docker Hub") if you are using an older version of 
         :program:`Singularity`.
      
      .. raw:: html

         <h2>Interaction</h2>
      
      To shell into the container use:
      
      .. code-block::

         $ singularity shell miracl_latest.sif bash
      
      Use the ``-B`` flag to bind a data directory to the container:
      
      .. code-block::

         $ singularity shell -B /data:/data miracl_latest.sif bash
      
      .. SeeAlso::
         For running functions on clusters please check our 
         :program:`Singularity` tutorials for Compute Canada and Sherlock

   .. tab:: Local

      .. warning::
         Support for this installation method will be discontinued in future 
         versions of :program:`MIRACL`. We recommend to use :program:`Docker` 
         or :program:`Singularity` instead.

      Steps to setup/run :program:`MIRACL` on a Linux/macOS machine:

      .. code-block::

         $ git clone https://github.com/mgoubran/MIRACL.git miracl
      
      .. tip::
         Alternatively, you can download the zip file containg the repo and 
         uncompress it

      Next, change directories into the newly created :file:`miracl` folder:

      .. code-block::

         $ cd miracl
      
      Create your virtual :program:`MIRACL` environment and activate it:
      
      .. attention::
         To setup a virtual environment you need :program:`Anaconda` for 
         :program:`Python 2.7`. It can be downloaded from `their official 
         website <https://www.anaconda.com/distribution/#download-section>`_
      
      .. code-block::

         $ conda create --name miracl python=3.7.4 pip
         $ conda activate miracl
      
      Install dependencies:
      
      .. code-block::

         $ pip install -e .
      
      .. raw:: html

         <h2>ANTS & c3d</h2>
      
      Next, download the :file:`depends` folder from our 
      `Dropbox link <https://www.dropbox.com/sh/i9swdedx7bsz1s8/AABpDmmN1uqPz6qpBLYLtt8va?dl=0>`_ 
      and place it either inside the :file:`linux_depends` or 
      :file:`mac_depends` folder:
      
      .. code-block::

         $ mv ~/Downloads/depends.zip miracl/.
         $ cd miracl
         $ unzip depends.zip
         $ rm depends.zip
      
      This folder contains compiled versions of :program:`ANTS` and 
      :program:`c3d` for Linux or Mac OS. Before continuing, make sure to 
      change the permissions. 

      This can be done by running:
      
      .. code-block::

         $ chmod -R 755 <path/to/depends>/*
      
      In order to run the pipeline, some symbolic links must be added to 
      access certain commands. Inside the :file:`miracl` folder, run:
      
      .. code-block::

         $ sudo ln -s <path/to/depends>/ants/antsRegistrationMIRACL.sh /usr/bin/ants_miracl_clar && chmod +x /usr/bin/ants_miracl_clar
         $ sudo ln -s <path/to/depends>/ants/antsRegistrationMIRACL_MRI.sh /usr/bin/ants_miracl_mr && chmod +x /usr/bin/ants_miracl_mr
      
      Make sure :file:`<path/to/depends>` is replaced with the directory path 
      that leads to the :file:`depends` directory.

      .. raw:: html

         <h2>Allen atlas</h2>
      
      Place the :file:`atlases` folder (which got downloaded together with the 
      ``depends`` folder) inside the :file:`miracl` folder:
      
      .. code-block::

         $ mv ~/Downloads/atlases.zip miracl/.
         $ cd miracl
         $ unzip atlases.zip
         $ rm atlases.zip
      
      This folder contains the Allen Atlas data needed for registration and 
      connectivity analysis.

      .. raw:: html

         <h2>Fiji & FSL</h2>
      
      .. raw:: html

         <h3>Install Fiji & FSL</h3>
      
      First, download :program:`Fiji/ImageJ` `from their offical 
      website <https://imagej.net/Fiji/Downloads>`_.

      Then do:
      
      .. code-block::

         $ cd depends
         $ wget https://downloads.imagej.net/fiji/latest/fiji-linux64.zip
         $ unzip fiji-linux64.zip
         $ rm fiji-linux64.zip
      
      Next, install additional plugins by going to ``Help -> Update`` and 
      clicking on the ``Manage update sites`` button.
      
      Choose the following update sites:
      
      - 3D ImageJ Suite: http://sites.imagej.net/Tboudier
      - Biomedgroup: https://sites.imagej.net/Biomedgroup
      - IJPB-plugins: http://sites.imagej.net/IJPB-plugins
      
      Download `FSL <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation>`_
      and install it:

      .. code-block::

         $ wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
         $ sudo python fslinstaller.py
      
      .. raw:: html

         <h2>Visualization</h2>
      
      For the visualization of nifti files and labels we recommend 
      `ITKSNAP <http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3>`_
      or the `nifti plugin <https://imagej.nih.gov/ij/plugins/nifti.html>`_ 
      for :program:`Fiji/ImageJ`.

      .. raw:: html

         <h2>Diffusion Data</h2>
      
      If you have diffusion MRI data download and install 
      `MRtrix3 <http://www.mrtrix.org/>`_:
      
      .. code-block::

         $ sudo apt-get install git g++ python python-numpy libeigen3-dev zlib1g-dev libqt4-opengl-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev
         $ git clone https://github.com/MRtrix3/mrtrix3.git
         $ cd mrtrix3
         $ ./configure
         $ ./build
         $ ./set_path
      
      .. raw:: html

         <h2>Deactivate</h2>
      
      To end a :program:`MIRACL` session, deactivate your virtual environment:
      
      .. code-block::

         $ conda deactivate
      
      .. raw:: html

         <h2>Update MIRACL</h2>
      
      To update :program:`MIRACL`, navigate into your :program:`MIRACL` base
      folder (e.g. ``$ cd miracl``) and run:
      
      .. code-block::

         $ git pull
      
      You should be good to go!

   .. tab:: Windows

      .. warning::
         Support for installing :program:`MIRACL` locally in the WSL will be 
         discontinued in future versions of :program:`MIRACL`. We recommend to 
         use :program:`Docker` or :program:`Singularity` instead.

      To install :program:`MIRACL` on your Windows system, Windows Subsystem 
      for Linux (WSL) must be installed. 
      `WSL2 <https://docs.microsoft.com/en-us/windows/wsl/compare-versions>`_
      is preferred. From there, the usual steps to install :program:`MIRACL` on 
      a Linux based system will be used with a few tweaks.
      
      .. hint::
         Follow the below steps if you want to install :program:`MIRACL` in 
         your WSL instance locally. If you prefer to use :program:`Docker` to 
         run :program:`MIRACL` on Windows follow our installation instructions 
         for :program:`Docker` instead.
      
      .. raw:: html

         <h2>Installing WSL 2 on Windows</h2>
      
      The Windows Subsystem for Linux (WSL) creates an environment that allows 
      users to run versions of Linux without having to set up a virtual 
      machine or a different computer.
      
      To install WSL, users can follow the 
      `instructions <https://docs.microsoft.com/en-us/windows/wsl/install>`_ 
      from Microsoft. More comprehensive instructions can be found 
      `here <https://www.windowscentral.com/install-windows-subsystem-linux-windows-10>`_. 
      Upgrading from WSL 1 to WSL 2 is recommended, due to 
      `WSL 2's benefits <https://docs.microsoft.com/en-us/windows/wsl/compare-versions>`_.

      .. raw:: html

         <h2>Install the Ubuntu distribution (Ubuntu 22.04) from the Microsoft Store</h2>
      
      .. note::
         You may ignore this step if you have a preferred Linux distribution 
         that is already installed in your WSL2
      
      A Linux distribution (distro), like Ubuntu, is an operating system based 
      on the Linux kernel.
      
      Now that WSL (either 1 or 2) is installed, the :program:`Ubuntu 22.04` 
      distro can be installed. To install Ubuntu, open the Windows Store app, 
      search for ":program:`Ubuntu 22.04`", and select the ``Get`` button. You 
      could also use this 
      `link <https://www.microsoft.com/en-gb/p/ubuntu-2004-lts/9n6svws3rx71>`_.

      .. raw:: html

         <h2>Install Python and pip</h2>
      
      The Ubuntu distro should have :program:`Python 3` installed. To ensure 
      that this is the case, update all packages installed in the WSL:
      
      .. code-block::

         $ sudo apt update
         $ sudo apt -y upgrade
      
      We can see which version of :program:`Python 3` is installed by typing:
      
      .. code-block::

         $ python3 -V
      
      The output in the terminal window will show the version number.
      
      :program:`pip` is required to install software packages in 
      :program:`Python`. It can be installed by running the following command:
      
      .. code-block::

         $ sudo apt install -y python3-pip
      
      You could also use :program:`Anaconda` to install the packages but we 
      found that installing and using pip was more straightforward.

      .. raw:: html

         <h2>Install MIRACL using local installation instructions</h2>
      
      To actually install :program:`MIRACL`, follow the local installation 
      instructions for Linux and macOS.

      .. raw:: html

         <h2>Installing Xming</h2>
      
      To use :program:`MIRACL's` graphical user interface (GUI), 
      :program:`Xming` must be installed. :program:`Xming` is a display server 
      for Windows computers, that is available for use by anyone. It can be 
      downloaded from `SourceForge <https://www.google.com/url?q=https://sourceforge.net/projects/xming/&source=gmail&ust=1641769602186000&usg=AOvVaw2MoTURhTsyCk_-56M3Qljj>`_.
      
      Before running :program:`MIRACL's` GUI, run Xming. In the terminal window 
      where :program:`MIRACL's` GUI will be run, input the following command:
      
      .. code-block::

         $ export DISPLAY=$DISPLAY:localhost:0
      
      .. raw:: html

         <h2>Running MIRACL with WSL 2</h2>
      
      Now that everything is installed, :program:`MIRACL` can be run via the 
      WSL. To run:
      
      #. Open WSL via terminal
      #. Navigate to the folder where you would like to run MIRACL from
      #. Activate the environment containing ``miracl``:
      
      .. code-block::

         $ source activate miracl
         $ miraclGUI

      .. raw:: html

         <h2>Jupyter notebook</h2>

      .. |linktoworkshop| replace:: :doc:`here <../downloads/workshops/2024/stanford_20_03_2024/stanford_20_03_2024>`

      .. include:: ../directives/tutorial_notebook_links.txt

