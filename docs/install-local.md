# Local Install
Steps to setup/run MIRACL on a Linux / Mac OS X machine:

    git clone https://github.com/mgoubran/MIRACL.git miracl

(or download the zip file containg the repo and uncompress it), then:

    cd miracl

To setup a virtual environment, download Anaconda for Python 2.7:
https://www.anaconda.com/distribution/#download-section,

Then create the environment:

    conda create --name miracl python=2.7.17 pip

    conda activate miracl

install Dependencies

    pip install -e .


#### PyQT
install PyQt4 using anaconda, run:
        
    conda install pyqt=4 -c anaconda

#### ANTS & c3d

Place the **depends** folder inside **linux_depends** or **mac_depends** (based on your OS), found here:

[download link](https://stanfordmedicine.box.com/s/og3czc5wgva41rmi52gkmjhk0y9bcg56)

inside the **miracl** folder

    mv ~/Downloads/depends.zip miracl/.
    cd miracl
    unzip depends.zip
    rm depends.zip

This folder contains compiled versions of **ANTS** and **c3d** for Linux or Mac OS. Before continuing, make sure to change the permissions. This can be done by running

    chmod -R 755 {path/to/depends}/*

In order to run the pipeline, some symbolic links must be added to access certain commands. Inside the **miracl** folder, run:

    sudo ln -s {path/to/depends}/ants/antsRegistrationMIRACL.sh /usr/bin/ants_miracl_clar && chmod +x /usr/bin/ants_miracl_clar
    sudo ln -s {path/to/depends}/ants/antsRegistrationMIRACL_MRI.sh /usr/bin/ants_miracl_mr && chmod +x /usr/bin/ants_miracl_mr

Make sure {path/to/depends} is replaced with the directory path that leads to the depends directory
.
#### Allen atlases

Place the **atlases** folder in the same link above inside the **miracl** folder

    mv ~/Downloads/atlases.zip miracl/.
    cd miracl
    unzip atlases.zip
    rm atlases.zip

This folder contains the Allen atlas data needed for registration and connectivity analysis

#### Fiji & FSL

install Fiji & FSL:

[Fiji/ImageJ](https://imagej.net/Fiji/Downloads)

for Linux:

    cd depends
    wget https://downloads.imagej.net/fiji/latest/fiji-linux64.zip
    unzip fiji-linux64.zip
    rm fiji-linux64.zip

install additional plugins by:

going to Help -> Update and press "Manage update sites" button and

choose the following update sites there:

    3D ImageJ Suite: http://sites.imagej.net/Tboudier
    Biomedgroup: https://sites.imagej.net/Biomedgroup
    IJPB-plugins: http://sites.imagej.net/IJPB-plugins


[FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

    wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
    sudo python fslinstaller.py


## Visualization

For the visualization of nifti files and labels we recommend [ITKSNAP](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3)

or the [nifti plugin](https://imagej.nih.gov/ij/plugins/nifti.html) for Fiji/ImageJ


## Diffusion Data

If you have diffusion MRI data install:

[MRtrix3](http://www.mrtrix.org)

    sudo apt-get install git g++ python python-numpy libeigen3-dev zlib1g-dev libqt4-opengl-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev
    git clone https://github.com/MRtrix3/mrtrix3.git
    cd mrtrix3
    ./configure
    ./build
    ./set_path

## Deactivate

To end session

    conda deactivate

## Update MIRACL

To update the package

    cd miracl
    git pull

____________________________


You should be good to go!

