FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y git wget build-essential g++ gcc cmake curl clang && \
    apt-get install -y libfreetype6-dev apt-utils pkg-config vim gfortran && \
    apt-get install -y binutils make linux-source unzip && \
    apt install -y libsm6 libxext6 libfontconfig1 libxrender1

# Install miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh && \
    bash Miniconda-latest-Linux-x86_64.sh -p /opt/miniconda -b && \
    rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/opt/miniconda/bin:${PATH}

RUN mkdir -p /code/atlases /data
WORKDIR /code

RUN apt install -y libhdf5-serial-dev && \
    conda install -y numpy matplotlib joblib scipy pandas && \
    conda install -y -c conda-forge tifffile && \
    conda install -y -c menpo opencv

# ANTS
RUN mkdir -p /opt/ANTs && \
    wget https://downloads.sourceforge.net/project/advants/ANTS/ANTS_Latest/ANTs-1.9.v4-Linux.sh?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fadvants%2Ffiles%2FANTS%2FANTS_Latest%2F -O ANTs-latest.sh && \
    chmod u+x ANTs-latest.sh && \
    ./ANTs-latest.sh --prefix=/opt/ANTs --skip-license

ENV ANTSPATH /opt/ANTs

# ImageJ / Fiji
WORKDIR /tmp
RUN wget http://downloads.imagej.net/fiji/latest/fiji-linux64.zip && \
    unzip fiji-linux64.zip && \
    mv Fiji.app/ /opt/fiji
ENV PATH $ANTSPATH/bin:/opt/fiji/bin:${PATH}

# Fiji Plugins
WORKDIR /opt/fiji/plugins
RUN wget https://github.com/ijpb/MorphoLibJ/releases/download/v1.4.0/MorphoLibJ_-1.4.0.jar && \
    wget https://github.com/thorstenwagner/ij-shape-filter/releases/download/v.1.4.2/ij_shape_filter-1.4.2.jar && \
    wget https://sites.imagej.net/Tboudier/plugins/mcib3d-suite/mcib3d_plugins.jar-20190201145530 && \
    mv mcib3d_plugins.jar-20190201145530 mcib3d_plugins.jar

# C3D
RUN wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64 /opt/cd3
ENV PATH /opt/cd3/bin:${PATH}

WORKDIR /code
RUN conda install -y cython h5py && \
    conda install -y pyqt=4 && \
    conda install -y pandas=0.19.2

ADD . /code
RUN git clone https://github.com/sergivalverde/nifti_tools && \
    mv nifti_tools /code/depends/NIFTI_TOOLS
ENV MIRACL_HOME=/code
RUN python /code/setup.py install

###############################################################################
#--- Allen atlas alias ----

WORKDIR /tmp
RUN git clone https://github.com/vsoch/MIRACLextra && \
    cd MIRACLextra && \
    mv ara /code/atlases/ara

ENV aradir "${MIRACL_HOME}/atlases/ara"

# Templates (atlas images)
ENV allen10 "${MIRACL_HOME}/atlases/ara/template/average_template_10um.nii.gz"
ENV allen25 "${MIRACL_HOME}/atlases/ara/template/average_template_25um.nii.gz"
ENV allen50 "${MIRACL_HOME}/atlases/ara/template/average_template_50um.nii.gz"

# Annotations (labels)
ENV lbls10 "${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_10um.nii.gz"
ENV lbls25 "${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_25um.nii.gz"
ENV lbls50 "${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_50um.nii.gz"

# Grand-parents labels
ENV gplbls25="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_25um_parent-level_3.nii.gz"
ENV gplbls50="${MIRACL_HOME}/atlases/ara/annotation/annotation_hemi_combined_50um_parent-level_3.nii.gz"

# ITK-snap LUT
ENV snaplut "${MIRACL_HOME}/atlases/ara/ara_snaplabels_lut.txt"
# Freeview LUT
ENV freelut "${MIRACL_HOME}/atlases/ara/ara_freeviewlabels_lut.txt"
################################################################################

RUN chmod u+x /code/run.sh

CMD ["/code/run.sh"]
ENTRYPOINT ["/opt/miniconda/bin/miracl"]
