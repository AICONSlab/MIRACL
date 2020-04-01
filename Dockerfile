ARG MIRACL_VERSION=latest
FROM mgoubran/miracl:base-$MIRACL_VERSION

ADD . /code
RUN git clone https://github.com/sergivalverde/nifti_tools && \
    mv nifti_tools /code/depends/NIFTI_TOOLS
ENV MIRACL_HOME=/code/miracl
RUN pip install -e /code/

###############################################################################
#--- Allen atlas alias ----

WORKDIR /tmp
RUN mkdir -p "/code/atlases/ara"
RUN wget -nH -r --cut-dirs 3 --no-parent -A txt,json,csv,nii.gz -P /code/atlases/ara http://web.stanford.edu/group/zeinehlab/MIRACLextra/

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
RUN ln -s "/code/depends/ants/antsRegistrationMIRACL.sh" /usr/bin/ants_miracl_clar && \
    chmod +x /usr/bin/ants_miracl_clar
RUN ln -s "/code/depends/ants/antsRegistrationMIRACL_MRI.sh" /usr/bin/ants_miracl_mr && \
    chmod +x /usr/bin/ants_miracl_mr
ENV ANTSPATH "${ANTSPATH}:/code/depends/ants"

ENV IN_DOCKER_CONTAINER Yes

################################################################################

ENTRYPOINT ["/opt/miniconda/bin/miracl"]
