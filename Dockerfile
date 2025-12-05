ARG MIRACL_VERSION=latest
FROM mgoubran/miracl:revised-base-$MIRACL_VERSION

ADD . /code
# delete ruamel pkg
RUN rm -rf $(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")/ruamel* && \
    pip install markupsafe==2.0.1 && \
    # Install setuptools v65.6.0 as latest version (v67.0.0)
    # breaks parsing. Temporary fix only. In the long run,
    # scripts should be refactored to work with current version!
    pip install setuptools==65.6.0 && \
    pip install -e /code/ "botocore >= 1.20.110"
ENV MIRACL_HOME=/code/miracl
ENV ATLASES_HOME=/code/atlases
COPY ./utility_scripts /usr/bin
RUN chmod o+x /usr/bin/download_sample_data && \
    chmod o+x /usr/bin/run_mapl3_example

# Point to g++-5 for NiftyReg compilation
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 50 --slave /usr/bin/g++ g++ /usr/bin/g++-5

#--- Install NiftyReg ---
ARG NR_INSTALL_DIR=/opt/niftyreg
RUN mkdir -p /tmp/niftyreg_source && \
    git clone https://github.com/SuperElastix/niftyreg.git /tmp/niftyreg_source && \
    mkdir -p /tmp/niftyreg && \
    mkdir -p $NR_INSTALL_DIR
WORKDIR /tmp/niftyreg
RUN cmake \
    -D BUILD_ALL_DEP=ON \
    -D BUILD_SHARED_LIBS=OFF \
    -D BUILD_TESTING=OFF \
    -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=$NR_INSTALL_DIR \
    -D M_LIBRARY=/opt/miniconda/include \
    -D PNG_INCLUDE_DIR=/opt/miniconda/lib/libpng.so \
    -D USE_CUDA=OFF \
    -D USE_OPENCL=OFF \
    -D USE_OPENMP=ON \
    -D USE_SSE=ON \
    /tmp/niftyreg_source && \
    make && \
    make install && \
    rm -r /tmp/niftyreg && \
    rm -r /tmp/niftyreg_source
ENV PATH=$NR_INSTALL_DIR/bin:$PATH
ENV LD_LIBRARY_PATH=$NR_INSTALL_DIR/lib:$LD_LIBRARY_PATH

# Point back to latest GNU compiler (g++-9)
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9

###############################################################################
#--- Allen atlas alias ----

WORKDIR /tmp
RUN mkdir -p /code/atlases/ara && \
    wget -P /code/atlases https://www.dropbox.com/sh/j31vurlp6h4lvod/AAAIKpYJQizkAte3Ju5DZYj8a --content-disposition && \
    unzip /code/atlases/ara.zip -x / -d /code/atlases/ara

# RUN conda install -y --no-update-deps pyqt=5

# Add atlas ENV vars
ENV aradir "/code/atlases/ara"

# Templates (atlas images)
ENV allen10 "/code/atlases/ara/template/average_template_10um.nii.gz"
ENV allen25 "/code/atlases/ara/template/average_template_25um.nii.gz"
ENV allen50 "/code/atlases/ara/template/average_template_50um.nii.gz"

# Annotations (labels)
ENV lbls10 "/code/atlases/ara/annotation/annotation_hemi_combined_10um.nii.gz"
ENV lbls25 "/code/atlases/ara/annotation/annotation_hemi_combined_25um.nii.gz"
ENV lbls50 "/code/atlases/ara/annotation/annotation_hemi_combined_50um.nii.gz"

# Grand-parents labels
ENV gplbls25="/code/atlases/ara/annotation/annotation_hemi_combined_25um_parent-level_3.nii.gz"
ENV gplbls50="/code/atlases/ara/annotation/annotation_hemi_combined_50um_parent-level_3.nii.gz"

# ITK-snap LUT
ENV snaplut "/code/atlases/ara/ara_snaplabels_lut.txt"
# Freeview LUT
ENV freelut "/code/atlases/ara/ara_freeviewlabels_lut.txt"

# ANTs commands
RUN ln -sf "/code/depends/ants/antsRegistrationMIRACL.sh" /usr/bin/ants_miracl_clar && \
    chmod +x /usr/bin/ants_miracl_clar
RUN ln -sf "/code/depends/ants/antsRegistrationMIRACL_MRI.sh" /usr/bin/ants_miracl_mr && \
    chmod +x /usr/bin/ants_miracl_mr
ENV ANTSPATH "${ANTSPATH}:/code/depends/ants"

ENV IN_DOCKER_CONTAINER Yes

###############################################################################
#--- ACE models ---

# Change permissions of models folder
RUN chmod -R 777 /code/miracl/seg/models
# Download UNet
RUN wget -O /code/miracl/seg/models/unet/best_metric_model.pth https://huggingface.co/AICONSlab/ACE/resolve/main/models/unet/best_metric_model.pth?download=true && \
    ls -l /code/miracl/seg/models/unet
#Download UNETR
RUN wget -O /code/miracl/seg/models/unetr/best_metric_model.pth https://huggingface.co/AICONSlab/ACE/resolve/main/models/unetr/best_metric_model.pth?download=true && \
    ls -l /code/miracl/seg/models/unetr

###############################################################################

# Install UV and make available system wide
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv $HOME/.local/bin/uv* /usr/local/bin/

###############################################################################
#--- Docker X11 forwarding directives ---

#STARTUNCOMMENT#
#STOPUNCOMMENT#

################################################################################

USER root
RUN mkdir -p /venvs && chown -R $USER:$USER /venvs
USER $USER

# Install Python 3.11 in a Conda venv and create Skeletonization venv 
RUN rm -rf /venvs/mapl3-skeletonization || true && \
    rm -rf /venvs/python311 || true && \
    cd /venvs && \
    pwd && \
    conda create -y -p /venvs/python311 python=3.11 && \
    # export PATH="/venvs/python311/bin:$PATH" && \
    uv init mapl3-skeletonization --python /venvs/python311/bin/python3.11 && \
    cd mapl3-skeletonization && \
    pwd && \
    ls -l && \
    uv add "cucim-cu12==25.4.0" \
    "cupy-cuda12x==13.4.1" \
    "cuvs-cu12==25.4.0" \
    "pylibraft-cu12==25.4.0" \
    "imagecodecs==2023.9.18" \
    "joblib==1.4.2" \
    "networkx==3.2.1" \
    "numpy==1.26.3" \
    "pandas==2.2.3" \
    "scikit-image==0.22.0" \
    "scipy==1.11.4" \
    "tifffile==2023.12.9"

USER root
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb && \
    dpkg -i cuda-keyring_1.1-1_all.deb && \
    apt-get update && \
    # apt-get install -y cuda-cudart-12-4 \
    # cuda-nvrtc-12-4 \
    # libcublas-12-4 \
    # libcusolver-12-4 \
    # libcusparse-12-4 \
    # libcurand-12-4 && \
    # apt-get install -y cuda-nvcc-12-4
    apt-get install -y cuda-cudart-12-4=12.4.127-1 \
    cuda-cudart-dev-12-4=12.4.127-1 \
    cuda-nvrtc-12-4=12.4.127-1 \
    libcublas-12-4=12.4.5.8-1 \
    libcurand-12-4=10.3.5.147-1 \
    libcusolver-12-4=11.6.1.9-1 \
    libcusparse-12-4=12.3.1.170-1 && \
    apt-get install -y cuda-nvcc-12-4=12.4.131-1



USER $USER
WORKDIR /home/$USER

# Temporarily uncommented to allow interactive shell access to Docker container
#ENTRYPOINT ["/opt/miniconda/bin/miracl"]
