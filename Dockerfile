FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y git wget build-essential g++ gcc cmake curl clang
RUN apt-get install -y libfreetype6-dev apt-utils pkg-config vim gfortran
RUN apt-get install -y binutils make linux-source unzip

# Install miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /opt/miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/opt/miniconda/bin:${PATH}

RUN mkdir /code
RUN mkdir /data
WORKDIR /code
ADD . /code

RUN conda install -y numpy matplotlib joblib scipy pandas
RUN conda install -y -c conda-forge tifffile
RUN conda install -y -c menpo opencv

# ANTS
RUN mkdir -p /opt/ANTs
RUN wget https://downloads.sourceforge.net/project/advants/ANTS/ANTS_Latest/ANTs-1.9.v4-Linux.sh?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fadvants%2Ffiles%2FANTS%2FANTS_Latest%2F -O ANTs-latest.sh
RUN chmod u+x ANTs-latest.sh
RUN ./ANTs-latest.sh --prefix=/opt/ANTs --skip-license
ENV ANTSPATH /opt/ANTs

# ImageJ / Fiji
WORKDIR /tmp
RUN wget http://downloads.imagej.net/fiji/latest/fiji-linux64.zip
RUN unzip fiji-linux64.zip
RUN mv Fiji.app/ /opt/fiji
ENV PATH $ANTSPATH/bin:/opt/fiji/bin:${PATH}

# C3D
RUN wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64 /opt/cd3
ENV PATH /opt/cd3/bin:${PATH}

WORKDIR /code
RUN conda install -y cython h5py
RUN conda install -y pyqt=4
RUN conda install -y pandas=0.19.2

# MRITrix
WORKDIR /opt
RUN apt-get install -y libeigen3-dev zlib1g-dev libqt4-opengl-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev
RUN git clone https://github.com/MRtrix3/mrtrix3.git && cd mrtrix3 && ./configure
ENV PATH /opt/mrtrix3/bin:${PATH}

WORKDIR /code
RUN git clone https://github.com/sergivalverde/nifti_tools
RUN mv nifti_tools /code/depends/NIFTI_TOOLS
ENV MIRACL_HOME=/code
RUN python /code/setup.py install

###############################################################################
#--- Allen atlas alias ----
# NOTE to @mirabel - we need to put this somewhere to download with wget/curl
#export aradir="${MIRACL_HOME}/atlases/ara"

# Templates (atlas images)
ENV allen10="${MIRACL_HOME}/atlases/ara/template/average_template_10um.nii.gz"
ENV allen25="${MIRACL_HOME}/atlases/ara/template/average_template_25um.nii.gz"
ENV allen50="${MIRACL_HOME}/atlases/ara/template/average_template_50um.nii.gz"

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
################################################################################


RUN chmod u+x /code/run.sh

CMD ["/code/run.sh"]
ENTRYPOINT ["/opt/miniconda/bin/miracl"]
