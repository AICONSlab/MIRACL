ACE Cluster Only
################

Apply cluster-wise analysis including a cluster-wise TFCE test and correlation analysis on voxelized and warped segmentation maps.



Main Inputs
============
Control and Treated directories, containing voxelized and warped segmentation maps for each group.


CLI
===

To get more information about the workflow and its required arguments 
use the following command on the CLI:

.. code-block::

   $ miracl stats ace -h













Example usage (`link to sample data <https://drive.google.com/drive/folders/1IgN9fDEVNeeT0a_BCzy3nReJWfxbrg72>`_):
==================================================================================================================

.. code-block::

   $ miracl stats ace \
        --control ./ctrl/ \
        --treated ./treated/ \
        --sa_output_folder ./output_dir \
        --sctp_num_perm 1000 \
        --rwc_voxel_size 25 \
        --sctp_smoothing_fwhm 3 \
        --sctp_tfce_start 0.05 \
        --sctp_tfce_step 5 \
        --sctp_tfce_h 2 \
        --sctp_tfce_e 0.5 



===================================  ======================  ==================  ===========================================================  =================================
Flag                                 Parameter               Type                Description                                                  Default
===================================  ======================  ==================  ===========================================================  =================================
\-c, \-\-control                     CONTROL_BASE_DIR        ``str``             path to base control directory                               ``None`` (required)
\-t, \-\-treated                     TREATED_BASE_DIR        ``str``             path to base treated directory                               ``None`` (required)
\-sao, \-\-sa_output_folder          SA_OUTPUT_FOLDER        ``str``             path to output directory                                     ``None`` (required)
\-ua, \-\-u_atlas_dir                ATLAS_DIR               ``str``             path to atlas directory                                      ``os.environ.get(ARA_ENV, None)``
\-sctpn, \-\-sctp_num_perm           NUM_PERM                ``int``             number of permutations                                       ``100``                                                   
\-rwcv, \-\-rwc_voxel_size           IMG_RESOLUTION          ``int``             image resolution (atlas resolution 10 or 25 um)              ``25``
\-sctpfwhm, \-\-sctp_smoothing_fwhm  SMOOTHING_FWHM          ``int``             fwhm of Gaussian kernel in pixel                             ``3``
\-sctpstart, \-\-sctp_tfce_start     TFCE_START              ``float``           tfce threshold start                                         ``0.01``
\-sctpstep, \-\-sctp_tfce_step       TFCE_STEP               ``float``           tfce threshold step                                          ``10``
\-sctph, \-\-sctp_tfce_h             TFCE_H                  ``float``           tfce H power                                                 ``2``
\-sctpe, \-\-sctp_tfce_e             TFCE_E                  ``float``           tfce E power                                                 ``0.5``
\-sctpc, \-\-sctp_cpu_load           CPU_LOAD                ``float``           percent of cpus used for parallelization                     ``0.9``
\-sctpsp, \-\--sctp_step_down_p      STEP_DOWN_P             ``float``           step down p value                                            ``0.3``
\-sctpm, \-\-sctp_mask_thr           MASK_THR                ``int``             percentile to be used for binarizing difference of the mean  ``95``
===================================  ======================  ==================  ===========================================================  =================================

.. |linktoworkshop| replace:: :doc:`here <../../../downloads/workshops/2024/stanford_20_03_2024/stanford_20_03_2024>`

.. include:: ../../../directives/tutorial_notebook_links.txt
