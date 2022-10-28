ARG MIRACL_VERSION=latest
FROM mgoubran/miracl:base-$MIRACL_VERSION

ADD . /code
# delete ruamel pkg
RUN rm -rf $(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")/ruamel* && \
    pip install markupsafe==2.0.1 && \
    pip install -e /code/
ENV MIRACL_HOME=/code/miracl

###############################################################################
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
    -D CMAKE_INSTALL_PREFIX=/opt/niftyreg \
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

###############################################################################
#--- Allen atlas alias ----

WORKDIR /tmp
RUN mkdir -p /code/atlases/ara && \
    wget -P /code/atlases https://www.dropbox.com/sh/j31vurlp6h4lvod/AAAIKpYJQizkAte3Ju5DZYj8a --content-disposition && \
    unzip /code/atlases/ara.zip -x / -d /code/atlases/ara

# RUN conda install -y --no-update-deps pyqt=5

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

#STARTUNCOMMENT#
# Setup host user as container user
ARG USER_ID=$USER_ID
ARG GROUP_ID=$GROUP_ID
ARG USER=$USER

RUN addgroup --gid $GROUP_ID $USER
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID $USER

# Change owner of /code directory
RUN chown -R $USER:$USER /code

# Change to $USER
USER $USER
WORKDIR /home/$USER
#STOPUNCOMMENT#

################################################################################

# Temporarily uncommented to allow interactive shell access to Docker container
#ENTRYPOINT ["/opt/miniconda/bin/miracl"]

