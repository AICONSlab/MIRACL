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
        -c ./ctrl/ \
        -t ./treated/ \
        -sao ./output_dir \
        -n 1000 \
        -a ./atlas/ \
        -r 25 \
        -sfwhm 3 \
        -start 0.05 \
        -step 5 \
        -h 2 \
        -e 0.5 



===========================  ======================  ==================  ===========================================================  =======================
Flag                         Parameter               Type                Description                                                  Default
===========================  ======================  ==================  ===========================================================  =======================
\-c, \-\-control             CONTROL_BASE_DIR        ``str``             path to base control directory                               ``None`` (required)
\-t, \-\-treated             TREATED_BASE_DIR        ``str``             path to base treated directory                               ``None`` (required)
\-sao, \-\-sa_output_folder  SA_OUTPUT_FOLDER        ``str``             path to output directory                                     ``None`` (required)
\-n, \-\-num_perm            NUM_PERM                ``int``             number of permutations                                       ``100``                                                   
\-a, \-\-atlas_dir           ATLAS_DIR               ``str``             path to atlas directory                                      ``miracl_home``
\-r, \-\-img_resolution      IMG_RESOLUTION          ``int``             image resolution (atlas resolution 10 or 25 um)              ``25``
\-sfwhm, \-\-smoothing_fwhm  SMOOTHING_FWHM          ``int``             fwhm of Gaussian kernel in pixel                             ``3``
\-start, \-\-tfce_start      TFCE_START              ``float``           tfce threshold start                                         ``0.01``
\-step, \-\-tfce_step        TFCE_STEP               ``float``           tfce threshold step                                          ``10``
\-h, \-\-tfce_h              TFCE_H                  ``float``           tfce H power                                                 ``2``
\-e, \-\-tfce_e              TFCE_E                  ``float``           tfce E power                                                 ``0.5``
\-c, \-\-cpu_load            CPU_LOAD                ``float``           percent of cpus used for parallelization                     ``0.9``
\-p, \-\--step_down_p        STEP_DOWN_P             ``float``           step down p value                                            ``0.3``
\-m, \-\-mask_thr            MASK_THR                ``int``             percentile to be used for binarizing difference of the mean  ``95``
===========================  ======================  ==================  ===========================================================  =======================