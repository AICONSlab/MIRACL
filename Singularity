Bootstrap: docker
From: ubuntu:14.04

%setup
    mkdir -p $SINGULRITY_ROOTFS/code
    #TODO: need to get allen data somehow into depends

%environment
    DEBIAN_FRONTEND=noninteractive
    ANTSPATH=/opt/ANTs
    MIRACL_HOME=/code
    PATH=$ANTSPATH/bin:/opt/fiji/bin:/opt/mrtrix3/bin:/opt/cd3/bin:${PATH}
    PATH=/opt/miniconda/bin:${PATH}
    export DEBIAN_FRONTEND ANTSPATH PATH MIRACL_HOME

%runscript
    /bin/bash /code/run.sh
    exec /opt/miniconda/bin/miracl

%files
. /code

%post
    DEBIAN_FRONTEND=noninteractive
    apt-get update && apt-get install -y git wget build-essential g++ gcc cmake curl clang
    apt-get install -y libfreetype6-dev apt-utils pkg-config vim gfortran
    apt-get install -y binutils make linux-source unzip

    # Install miniconda
    curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
    bash Miniconda-latest-Linux-x86_64.sh -p /opt/miniconda -b
    rm Miniconda-latest-Linux-x86_64.sh
    PATH=/opt/miniconda/bin:${PATH}

    mkdir -p /data && cd /code

    conda install -y numpy matplotlib joblib scipy pandas
    conda install -y -c conda-forge tifffile
    conda install -y -c menpo opencv

    # ANTS
    mkdir -p /opt/ANTs
    wget https://downloads.sourceforge.net/project/advants/ANTS/ANTS_Latest/ANTs-1.9.v4-Linux.sh?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fadvants%2Ffiles%2FANTS%2FANTS_Latest%2F -O ANTs-latest.sh
    chmod u+x ANTs-latest.sh
    ./ANTs-latest.sh --prefix=/opt/ANTs --skip-license

    # ImageJ / Fiji
    cd /tmp
    wget http://downloads.imagej.net/fiji/latest/fiji-linux64.zip
    unzip fiji-linux64.zip
    mv Fiji.app/ /opt/fiji

    # C3D
    wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64 /opt/cd3

    conda install -y cython h5py
    conda install -y pyqt=4
    conda install -y pandas=0.19.2

    # MRITrix
    # cd /opt
    # apt-get install -y libeigen3-dev zlib1g-dev libqt4-opengl-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev
    # git clone https://github.com/MRtrix3/mrtrix3.git && cd mrtrix3 && ./configure

    cd /code
    python /code/setup.py install


#--- Allen atlas alias ----
# TODO: not sure where this came from
#export aradir="${MIRACL_HOME}/atlases/ara"

# Templates (atlas images)
#ENV allen10="${MIRACL_HOME}/atlases/ara/template/average_template_10um.nii.gz"
#ENV allen25="${MIRACL_HOME}/atlases/ara/template/average_template_25um.nii.gz"
#ENV allen50="${MIRACL_HOME}/atlases/ara/template/average_template_50um.nii.gz"

# Annotations (labels)
#export lbls10="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_10um.nii.gz"
#export lbls25="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_25um.nii.gz"
#export lbls50="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_50um.nii.gz"

# Grand-parents labels
#export gplbls25="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_25um_parent-level_3.nii.gz"
#export gplbls50="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_50um_parent-level_3.nii.gz"

# ITK-snap LUT
#export snaplut="${MIRACL_HOME}/atlases/ara/ara_snaplabels_lut.txt"
# Freeview LUT
#export freelut="${MIRACL_HOME}/atlases/ara/ara_freeviewlabels_lut.txt"

    chmod u+x /code/run.sh
