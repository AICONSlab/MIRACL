FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y git wget build-essential g++ gcc cmake curl clang && \
    apt-get install -y libfreetype6-dev apt-utils pkg-config vim gfortran && \
    apt-get install -y binutils make linux-source unzip && \
    apt install -y libsm6 libxext6 libfontconfig1 libxrender1 && \
    apt-get install itksnap

# Install miniconda
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda2-4.6.14-Linux-x86_64.sh && \
    bash Miniconda2-4.6.14-Linux-x86_64.sh -p /opt/miniconda -b && \
    rm Miniconda2-4.6.14-Linux-x86_64.sh
ENV PATH=/opt/miniconda/bin:${PATH}

RUN mkdir -p /code/atlases /data
WORKDIR /code

RUN apt install -y libhdf5-serial-dev && \
    pip install matplotlib joblib scipy==1.2.1 && \
    pip install tifffile && \
    pip install menpo opencv-python && \
    apt remove cmake && \
    pip install cmake

# Install ANTs
###   Install ANTs   ###
# The following installs a given version of ANTs:
# Specify where to install packages:
ENV ANTS_FOLDER=/usr/local/ANTs
# Grab the Github repository, checkout the needed version,
#   build
ARG ANTs_VERSION
RUN cd /tmp && \
    git clone https://github.com/ANTsX/ANTs.git && \
    cd ANTs && \
    git checkout ${ANTs_VERSION} && \
    buildDir=${PWD}/build && \
    mkdir -p $buildDir ${ANTS_FOLDER} && \
    cd $buildDir && \
    cmake \
        -DCMAKE_INSTALL_PREFIX=${ANTS_FOLDER} \
        -DBUILD_SHARED_LIBS=OFF \
    -DSuperBuild_ANTS_USE_GIT_PROTOCOL=OFF \
        -DBUILD_TESTING=OFF \
        -DRUN_LONG_TESTS=OFF \
        -DRUN_SHORT_TESTS=OFF \
        /tmp/ANTs 2>&1 | tee cmake.log && \
    make 2>&1 | tee build.log && \
    cd ${buildDir}/ANTS-build && \
    make install 2>&1 | tee install.log && \
    rm -r /tmp/ANTs

# Add ANTs/bin to the path:
ENV PATH=$ANTS_FOLDER/bin/:$PATH
ENV ANTSPATH=$ANTS_FOLDER/bin/

# ImageJ / Fiji
WORKDIR /tmp
RUN wget http://downloads.imagej.net/fiji/latest/fiji-linux64.zip && \
    unzip fiji-linux64.zip && \
    mv Fiji.app/ /opt/fiji && \
    rm fiji-linux64.zip && \
    ln -s /opt/fiji/ImageJ-linux64 /opt/fiji/Fiji

ENV PATH ${ANTSPATH}:/opt/fiji:${PATH}

# Fiji Plugins
WORKDIR /opt/fiji/plugins
RUN wget https://github.com/ijpb/MorphoLibJ/releases/download/v1.4.0/MorphoLibJ_-1.4.0.jar && \
    wget https://github.com/thorstenwagner/ij-shape-filter/releases/download/v.1.4.2/ij_shape_filter-1.4.2.jar && \
    wget https://sites.imagej.net/Tboudier/plugins/mcib3d-suite/mcib3d_plugins.jar-20190201145530 && \
    mv mcib3d_plugins.jar-20190201145530 mcib3d_plugins.jar

# C3D
RUN wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64 /opt/cd3 && \
    rm c3d-nightly-Linux-x86_64.tar.gz
ENV PATH /opt/c3d/bin:${PATH}

# Install FSL, cmake
RUN wget -O- http://neuro.debian.net/lists/trusty.us-tn.full | tee /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9 && \
    apt-get update && apt-get install -y fsl-5.0-core fsl && \
    apt remove cmake && \
    pip install cmake --upgrade

ENV FSLDIR="/usr/share/fsl/5.0" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    POSSUMDIR="/usr/share/fsl/5.0" \
    LD_LIBRARY_PATH="/usr/lib/fsl/5.0:$LD_LIBRARY_PATH" \
    FSLTCLSH="/usr/bin/tclsh" \
    FSLWISH="/usr/bin/wish" \
    POSSUMDIR="/usr/share/fsl/5.0"

ENV PATH="/usr/lib/fsl/5.0:${PATH}"

WORKDIR /code
RUN pip install scikit-image==0.14.2 && \
    pip install cython h5py && \
    pip install pandas==0.24.2

RUN conda install -y --no-update-deps pyqt=4
