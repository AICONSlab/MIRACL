FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y git wget build-essential g++ gcc cmake curl clang && \
    apt-get install -y libfreetype6-dev apt-utils pkg-config vim gfortran && \
    apt-get install -y binutils make linux-source unzip && \
    apt install -y libsm6 libxext6 libfontconfig1 libxrender1

# Install miniconda
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda-latest-Linux-x86_64.sh && \
    bash Miniconda-latest-Linux-x86_64.sh -p /opt/miniconda -b && \
    rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/opt/miniconda/bin:${PATH}

RUN mkdir -p /code/atlases /data
WORKDIR /code

RUN apt install -y libhdf5-serial-dev && \
    pip install numpy==1.15.4 && \
    pip install matplotlib joblib scipy && \
    pip install tifffile && \
    pip install menpo opencv-python

# ANTS
ENV ANTSPATH /opt/ANTs
RUN mkdir -p /opt/ANTs && \
    curl -sSL "https://dl.dropbox.com/s/2f4sui1z6lcgyek/ANTs-Linux-centos5_x86_64-v2.2.0-0740f91.tar.gz" \
    | tar -xzC $ANTSPATH --strip-components 1
#    wget https://downloads.sourceforge.net/project/advants/ANTS/ANTS_Latest/ANTs-1.9.v4-Linux.sh?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fadvants%2Ffiles%2FANTS%2FANTS_Latest%2F -O ANTs-latest.sh && \
#    chmod u+x ANTs-latest.sh && \
#    ./ANTs-latest.sh --prefix=/opt/ANTs --skip-license

# ImageJ / Fiji
WORKDIR /tmp
RUN wget http://downloads.imagej.net/fiji/latest/fiji-linux64.zip && \
    unzip fiji-linux64.zip && \
    mv Fiji.app/ /opt/fiji && \
    rm fiji-linux64.zip

ENV PATH ${ANTSPATH}:/opt/fiji/bin:${PATH}

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
ENV PATH /opt/cd3/bin:${PATH}

# Install FSL
RUN wget -O- http://neuro.debian.net/lists/trusty.us-tn.full | tee /etc/apt/sources.list.d/neurodebian.sources.list
RUN apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9

RUN apt-get update && apt-get install -y fsl-5.0-core fsl

ENV FSLDIR="/usr/share/fsl/5.0" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    POSSUMDIR="/usr/share/fsl/5.0" \
    LD_LIBRARY_PATH="/usr/lib/fsl/5.0:$LD_LIBRARY_PATH" \
    FSLTCLSH="/usr/bin/tclsh" \
    FSLWISH="/usr/bin/wish" \
    POSSUMDIR="/usr/share/fsl/5.0"

ENV PATH="/usr/lib/fsl/5.0":${PATH}

WORKDIR /code
RUN pip install scikit-image==0.14.2 && \
    pip install cython h5py && \
    pip install pandas==0.19.2

RUN conda install -y --no-update-deps pyqt=4
