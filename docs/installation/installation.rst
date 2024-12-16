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
   has been deprecated. Please use :program:`Docker` or :program:`Singularity`
   instead.

.. important::
   :program:`MIRACL` has been tested on:

   * **Docker**:

     * **Ubuntu**: ``20.04`` (Focal Fossa), ``22.04`` (Jammy Jellyfish), ``24.04`` (Noble Numbat)

     * **Debian**: ``13`` (trixie)

   * **Singularity**:

     * **Ubuntu**: ``20.04`` (Focal Fossa), ``22.04`` (Jammy Jellyfish), ``24.04`` (Noble Numbat)

     * **Gentoo**: ``2.14``

   * **Apptainer**:

     * **Ubuntu**: ``20.04`` (Focal Fossa)

     * **Gentoo**: ``2.14``

   We strongly recommend that you use one of the above Linux versions to run
   :program:`MIRACL`!

.. note::
   Hardware requirements for :program:`MIRACL` are heavily dependent on the 
   type/size of your data as well as the analyses you are running. While 
   some modules and datasets can be less computationally expensive, others 
   require a lot of resources. As a point of reference, the least powerful 
   system that we are testing :program:`MIRACL` on, uses a ``24-Core Threadripper`` 
   with ``128GB RAM`` and two ``NVIDIA RTX A6000 GPUs``.

.. tabs::

   .. tab:: Docker

      We provide a installation script to automatically create a :program:`Docker` 
      image for you that can be run using :program:`Docker Compose`. This 
      method does not require a manual installation of :program:`MIRACL` and 
      works on Linux and in the WSL2 on Windows. Theoretically, :program:`MIRACL`
      should also work on MacOS but we do not officially support it.

      .. tip::
         Docker is our recommended method for running :program:`MIRACL` on 
         local machines and servers

      Docker is well suited if you want to run :program:`MIRACL` on a local 
      machine or local server. If you need to run :program:`MIRACL` on a 
      cluster, see our instructions for installing :program:`Apptainer/Singularity`. 
      If you don't have Docker installed on your computer, do that first. Make 
      sure your installation includes :program:`Docker Compose` as it is 
      required to run the installation script we provide. Note that :program:`Docker 
      Compose` is included as part of the :program:`Docker Desktop` 
      installation by default.

      .. raw:: html

         <h2>Getting started</h2>

      First, it is important to understand how the container is built. There 
      is a base image in the ``docker`` folder that installs :program:`Python` 
      and dependencies. Then the ``Dockerfile`` in the base of the repository 
      builds the :program:`Docker` image from that base. When the build 
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

      .. _git clone target:

      .. code-block::

         $ git clone https://www.github.com/mgoubran/MIRACL

      Change into the newly created directory where you cloned 
      :program:`MIRACL` to:

      .. code-block::

         $ cd MIRACL

      Build the latest :program:`MIRACL` image using the installation script we 
      provide:

      .. code-block::

         $ ./install.sh

      .. attention::

         In order for the ``./install.sh`` script to work, :program:`Docker` 
         should **NOT** be used with ``sudo``. Our script checks and exits if 
         it is being run with ``sudo`` priviledges. The reason for this behavior 
         is that the installation script creates a user in the Docker container 
         that matches the ``uid`` and ``gid`` of the host user which is required
         correct X11 forwarding. This user should **NOT** be ``root`` which is 
         the case when :program:`Docker` commands are executed with ``sudo``. 
         For more information on how to add a ``docker`` user to use 
         :program:`Docker` without ``sudo`` visit the official :program:`Docker` 
         `documentation <https://docs.docker.com/engine/install/linux-postinstall/>`_.

      .. error::
         Make sure that the script can be executed. If it can't and you are 
         the owner of the file, use ``chmod u+x install.sh`` to make it 
         executable. Prefix the ``chmod`` command with ``sudo`` if you are not 
         the owner of the file or change permissions for ``g`` and/or ``o``.

      Running the script without any flags will start an interactive installation 
      process that will run you through an abbreviated version of the installation.

      .. code-block:: 

         $ ./install.sh
         No flags provided, starting interactive prompt...
         Enter Docker image name (default: 'miracl_mgoubran_kirk_4918_img'):
         Enter Docker container name (default: 'miracl_mgoubran_kirk_4918'):
         Enable GPU in Docker container (required for ACE) (y/N): y
         Enter the location of your data on your host system (default: None). If you choose a location, your data will be mounted at '/data' in your container: /data5/projects/


      Press enter for the image and container prompts to choose the default names
      or enter your preferred names. GPU forwarding will be disabled by default 
      so enter ``y``, ``Y``, ``Yes``, or ``YES`` at the prompt to enable it. 
      Lastly, you will be prompted for the location of your data on the host 
      system. Provide the full path to your location. It will be mounted under 
      ``/data`` in the container. Once you entered all prompts, :program:`MIRACL` 
      will be installed automatically.

      .. note::

         This installation method should be sufficient for 90% of users. However,
         If you require more fine grained control see our ``Additional build 
         options`` section further below.

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
      
      .. raw:: html

         <h2>Stopping the container</h2>
      
      Exit your container and navigate to your :program:`MIRACL` folder. Use 
      :program:`Docker Compose` to stop the container:
      
      .. code-block::

         $ docker compose down
      
      .. include:: ../directives/docker_compose_directive.rst

      .. raw:: html

         <h2>Mounting additional drives</h2>

      Files that are saved while using :program:`MIRACL` should be saved to 
      volumes mounted into the container in order to make them persistent. You 
      might have already mounted at least one data location when you used the 
      interactive installation menu or several if you used the flags outlined 
      in the ``Additional build options`` sections below. However, if you need
      to mount additional volumes, you can easily do that by adding them to the 
      ``docker-compose.yml`` in the base directory under the ``volumes`` section.
      
      Example:
      
      .. code-block::

         volumes:
               - '/home/mgoubran/.Xauthority:/home/mgoubran/.Xauthority'
               - '/home/mgoubran/mydata:/home/mgoubran/mydata'  # This is the additional volume

      .. danger::
         Do not delete the ``.Xauthority`` volume that is already mounted. It 
         mounts your ``.Xauthority`` file which is important for X11 to work 
         correctly.
      
      The format of mounting volumes is ``</host/path>:</container/path>`` (note
      that the delimiter is ``:`` but that there are no trailing ``/``). In the 
      above example, the host path ``/home/mgoubran/mydata`` is mounted to the 
      container path ``/home/mgoubran/mydata``. The names for the paths on the 
      host system do not need to match the names for the locations inside the 
      container. The above example could therefore also be ``/home/mgoubran/mydata:/data``.

      .. raw:: html

         <h2>Additional build options</h2>

      The interactive installation method described above should be sufficient
      90% of users. However, if you need more finegrained control or advanced
      options, use the flags described in this section.

      To start, use ``./install.sh -h`` to see all optional flags:

      .. code-block::

         Usage: ./install.sh [-n service_name] [-i image_name] [-c container_name] [-t {auto, x.x.x}] [-g] [-e] [-v vol:vol] [-l] [-s] [-m] [-h]

           Automatically build MIRACL Docker image with pseudo host user

         Options:

           -n, name of the Docker service (randomized default: 'miracl_mgrouban_hughes_11707')
           -i, specify image name (randomized default: 'miracl_mgrouban_hughes_11707_img')
           -c, specify container name (default: 'miracl')
           -t, set when using specific MIRACL tag/version. Use 'auto' to parse from 'miracl/version.txt' or specify version as floating point value in format 'x.x.x' (default: 'latest')
           -g, enable Nvidia GPU passthrough mode for Docker container which is required for some of MIRACL's scripts e.g. ACE segmentation (default: false)
           -e, disable mounting MIRACL's script directory into Docker container. Mounting is useful if you want host changes to propagate to the container directly (default: false; set flag to disable)
           -d, set shared memory (shm) size (e.g. '1024mb', '16gb' or '512gb') which is important for e.g ACE (default: int(MemTotal/1024)*0.85 of host machine)
           -v, mount volumes for MIRACL in docker-compose.yml, using a separate flag for each additional volume (format: '/path/on/host:/path/in/container'; default: none)
           -l, write logfile of build process to 'build.log' in MIRACL root directory (default: false)
           -s, print version of build script and exit
           -m, print version of MIRACL on current Git branch and exit
           -h, print this help menu and exit

         Script version: 2.0.1-beta
         MIRACL version: 2.4.0

      Let's have a closer look at the most important flags.

      .. raw:: html

         <h3>Image and container naming</h3>

      By default, the installation script will choose names for the image and
      container randomly, using the following syntax:

      .. code-block::

         <miracl>_<usernamehostuser>_<randomname>_<randomdigitsbetween0and99999>

      The image name will also be appended with ``<_img>`` do distinguish it
      from the container name. We do this to avoid conflicts with previous
      or dangling installations of :program:`MIRACL`. Is you are confident that
      you will not duplicate your image or container names, set the ``-i`` and
      ``-c`` flags to choose your preferred names:

      .. code-block::

         $ ./install.sh -i <image_name> -c <container_name>
      
      Example:
      
      .. code-block::

         $ ./install.sh -i josmann/miracl_dev_img -c miracl_dev
      
      .. raw:: html

         <h3>GPU forwarding</h3>

      If you want to add GPU (Nvidia/CUDA) support to your :program:`MIRACL`
      container, you can do so by running the installation script with the ``-g`` 
      flag:

      .. code-block::

         $ ./install.sh -g

      This is required for :program:`MIRACL` modules like :doc:`ACE <../tutorials/workflows/ace_flow/ace_flow>`.

      .. raw:: html

         <h3>Disable script directory mounting</h3>
         
      Our installation script mounts the ``miracl`` folder from inside your 
      cloned :program:`MIRACL` Git folder by default. The ``miracl`` folder 
      contains all of :program:`MIRACL's` modules and workflow code. This 
      behavior is useful when you want to make real-time changes to e.g. a module for 
      fit your specific needs on the fly as the changes will persist across 
      restarts. In case this behavior is not desired, e.g. when testing changes 
      that you don't want to be permanent, use the ``-e`` flag to disable 
      automatic mounting.

      .. raw:: html

         <h3>Set shared memory size</h3>

      It is not always desirable to let your host system share all of its 
      available memory with the :program:`MIRACL` container. By default, 
      the memory that will be shared by :program:`MIRACL` is calculated as
      follows:

      .. code-block::

         int(MemTotal/1024)*0.85 of host machine

      If you want to increase or limit the memory availabe to :program:`MIRACL`,
      set it manually using the ``-d`` flag. Example sizes are ``1024mb``, 
      ``16gb``, or ``512gb``.

      Example:

      .. code-block::

         $ ./install.sh -d 512gb

      This will set the shared memory size to ``512gb``.

      .. raw:: html

         <h3>Mount additional volumes</h3>

      Use the ``-v`` flag if you need to mount several volumes or files from 
      your host system to your :program:`MIRACL` :program:`Docker` container.
      Use a separate flag for each additional volume with this format: 
      ``-v '/path/on/host:/path/in/container'``. Make sure that you use a 
      separate ``-v`` flag for each separate volume!

      Example:

      .. code-block::

         $ ./install -v /data5:/data5 -v /configfile:/configfile -v /data4:/additional_data

      This will automatically add the volumes to your ``docker-compose.yml`` 
      configuration under the ``volumes`` section where you can further edit 
      or remove them as needed.

      .. hint::

         Combine any of the above flags if you want to use several of them 
         together e.g.:

         .. code-block::
        
           $ ./miracl -i josmann/miracl_dev_img -c miracl_dev -g -v /data:/data -v /config:/config

      .. raw:: html

         <h3>MIRACL versions</h3>
      
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
         build the image for your chosen version by running the installation
         script with the ``-t`` flag:
      
      .. code-block::

         $ ./install.sh -t
      
      .. note::
         If you want to build an image for a version of MIRACL <= ``2.2.4`` 
         either follow the build instructions of the particular version or 
         download the latest installation script using e.g. 
         ``wget https://raw.githubusercontent.com/AICONSlab/MIRACL/master/install.sh``
         (overwrites current installation script if present) and run it with 
         the ``-t`` flag.
      
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

   .. tab:: Windows (WSL2)

      .. warning::
         Support for installing :program:`MIRACL` **locally** in the 
         :program:`WSL` has been deprecated in version ``2.2.6`` of 
         :program:`MIRACL`. The recommended way to install :program:`MIRACL`
         on Windows is to use Docker in the :program:`WSL`.

      The Windows Subsystem for Linux (:program:`WSL`) creates an environment 
      that allows users to run versions of :program:`Linux` without having to 
      set up a virtual machine or a different computer.
      
      .. important::
         :program:`Docker Desktop` requires :program:`WSL` version ``1.1.3.0`` 
         or later to be installed and turned on. To check open a command prompt 
         in Windows (``cmd``) and type: ``wsl --status``.

      To install WSL, users can follow the instructions from 
      `Microsoft <https://docs.microsoft.com/en-us/windows/wsl/install>`_.
      More comprehensive instructions can be found
      `here <https://www.windowscentral.com/install-windows-subsystem-linux-windows-10>`__.
      Upgrading from :program:`WSL1` to :program:`WSL2` is recommended, due to 
      :program:`WSL2`’s `benefits <https://docs.microsoft.com/en-us/windows/wsl/compare-versions>`_.

      Once the :program:`WSL` has been installed you can proceed to install
      :program:`Docker`.

      .. note::
         You may ignore the next step if you have a preferred, :program:`Docker`
         enabled Linux distribution that is already installed in your 
         :program:`WSL2`.

      .. raw:: html

         <h2>Installing Docker on Windows</h2>
      
      1. Download the :program:`Docker Desktop` installer for Windows from 
         `here <https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe>`__ 
         or from the `release notes <https://docs.docker.com/desktop/release-notes/>`_.
      2. Double-click :program:`Docker Desktop Installer.exe` to run the 
         installer. By default, :program:`Docker Desktop` is installed at 
         ``C:\Program Files\Docker\Docker``.

      .. attention::
         By default, :program:`WSL2` should be used with :program:`Docker Desktop`.
         However, if your Windows system supports :program:`WSL2` *and* 
         :program:`Hyper-V`, make sure to select the :program:`WSL2` option on 
         the Configuration page when prompted.

      3. Follow the instructions on the installation wizard to authorize the 
         installer and proceed with the install.
      4. When the installation is successful, select ``Close`` to complete the 
         installation process. 

      .. tip::
         Technically, :program:`Docker` can be run on the Windows command 
         prompt. However, it is recommended to use :program:`Docker` in a Linux 
         distro installed in the :program:`WSL`.

      5. Open the :program:`WSL2` on Windows in a command prompt (``cmd``). 
         Check the drop down menu next to the tab for installed Linux versions 
         or type ``wsl -l -v``.

         a. **`Ubuntu` is already installed**: Select it from the drop down.
            An :program:`Ubuntu` terminal will open in a new tab.

         b. **`Ubuntu` is not yet installed**: Open the
            :program:`Microsoft Store` and search for :program:`Ubuntu`. 
            Choose the version you want to install and click the ``Get`` button 
            to automatically install it on the :program:`WSL`. Select the 
            version you installed from the drop down next to the command prompt 
            tab. An :program:`Ubuntu` terminal will open in a new tab.

      6. Open :program:`Docker Desktop` and navigate to ``Settings``. In the
         ``General`` tab check if ``Use the WSL 2 based engine`` checkbox is 
         checked. Check it if it isn't yet.
      7. Still in the ``Settings`` navigate to ``Resources>WSL integration``.
         Enable the :program:`Ubuntu` distribution that you want to use
         :program:`Docker` with.
      8. Go back to the command prompt and open the :program:`Docker` enabled 
         :program:`Ubuntu` distro in a new tab.
      9. In the Linux terminal, type ``docker run hello`` to check if 
         :program:`Docker` is working correctly. 

      .. raw:: html
         
         <h2>Install MIRACL in the WSL2</h2>

      Just follow our installation instructions for :program:`Docker` to 
      install :program:`MIRACL` as a :program:`Docker` container in the
      :program:`WSL2`.

      .. hint::
         Follow the below steps if you want to install :program:`MIRACL` in 
         your WSL instance locally. If you prefer to use :program:`Docker` to 
         run :program:`MIRACL` on Windows follow our installation instructions 
         for :program:`Docker` instead.

   .. tab:: Local (deprecated)

      .. warning::
         Support for this installation method has been discontinued starting
         with version of ``2.2.6`` of :program:`MIRACL`. Please use :program:`Docker` 
         or :program:`Singularity` instead.

      .. warning::
         THIS INSTALLATION METHOD HAS BEEN DEPRECATED!

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

