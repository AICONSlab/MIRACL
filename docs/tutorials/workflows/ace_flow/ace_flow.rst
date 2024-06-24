ACE Workflow
############

**A**\ I-based **C**\ artography of **E**\ nsembles (**ACE**) pipeline highlights:

1. Cutting-edge vision transformer and CNN-based DL architectures trained on 
   very large LSFM datasets (`link to sample data <https://drive.google.com/drive/folders/14xWysQshKxwuTDWEQHT3OGKcH16scrrQ>`__
   and :ref:`refer to example section<example_anchor>`) to map brain-wide local/laminar neuronal activity.
2. Optimized cluster-wise statistical analysis with a threshold-free 
   enhancement approach to chart subpopulation-specific effects at the laminar 
   and local level, without restricting the analysis to atlas-defined regions 
   (`link to sample data <https://drive.google.com/drive/folders/1IgN9fDEVNeeT0a_BCzy3nReJWfxbrg72>`__ 
   and :ref:`refer to example section<example_anchor>`).
3. Modules for providing DL model uncertainty estimates and fine-tuning (in a future release).
4. Interface with MIRACL registration.
5. Ability to map the connectivity between clusters of activations.

Installation
============

To install the ACE workflow, refer to the MIRACL installation guide and video tutorials:

- :doc:`Installation guide <../../../installation/installation>`

- `Video tutorial <https://www.google.ca/>`_

.. TODO: update the tutorial link

.. note::

   Make sure that you set the GPU option during installation using the ``-g`` flag.
   Once the installation is complete, enter the ``docker`` container using ``docker exec -it <CONTAINER_NAME> bash``
   and run the ``nvidia-smi`` command to ensure your GPU is detected.

The ACE workflow can only be run with pre-trained DL models. To get access to these models please reach out
to `a.attarpour@mail.utoronto.ca <mailto:a.attarpour@mail.utoronto.ca>`_.

These models will be included by default in a future release once ACE is published.

.. note::
   
   The DL models must be in a specific directory structure to be used by the ACE workflow.

   Once you have the models, place them in the required directory structure by using the following commands:

   .. code-block::

      cp <PATH TO UNET MODEL FILE> <WHERE YOU CLONED MIRACL>/miracl/seg/models/unet/best_metric_model.pth
      cp <PATH TO UNETR MODEL FILE> <WHERE YOU CLONED MIRACL>/miracl/seg/models/unetr/best_metric_model.pth

   The path <WHERE YOU CLONED MIRACL> is the path where you cloned the MIRACL repository. This is the
   location where you ran these :ref:`installation steps <git clone target>`.

   To check that the models are in the correct directory structure, run the following commands:

   .. code-block::

      ls <WHERE YOU CLONED MIRACL>/miracl/seg/models/unet/best_metric_model.pth
      ls <WHERE YOU CLONED MIRACL>/miracl/seg/models/unetr/best_metric_model.pth

   The output should be similar to the following:

   .. code-block::

      best_metric_model.pth
      best_metric_model.pth


Main Inputs
============

Mode 1: Running ACE for two groups
- Control and Treated directories, containing whole-brain 3D LSFM datasets for multiple subjects.

OR

Mode 2: Running ACE for a single subject
- A single directory containing a single subject's whole-brain 3D LSFM dataset.

Command Line Interface (CLI)
============================

To use the CLI, you must first enter the docker container by running the following command:

.. code-block::

   $ docker exec -it <CONTAINER_NAME> bash

To get more information about the workflow and its required arguments 
use the following command on the cli:

.. code-block::

   $ miracl flow ace -h

The following information will be printed to the terminal:

.. code-block::   
   
   usage: miracl flow ace
        [-s SINGLE_TIFF_DIR]
        [-c CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE]
        [-t TREATED_BASE_DIR TREATED_TIFF_DIR_EXAMPLE]
        -sao SA_OUTPUT_FOLDER
        -sam {unet,unetr,ensemble}
        -sar X-res Y-res Z-res
        [-sag SA_GPU_INDEX]
        [-ctnd CTN_DOWN]
        [-rcao RCA_ORIENT_CODE]
        [-rcav {10,25,50}]
        [-rvad RVA_DOWNSAMPLE]
        [-rwcv {10,25,50}]
        [--rerun-registration TRUE/FALSE]
        [--rerun-segmentation TRUE/FALSE]
        [--rerun-conversion TRUE/FALSE]

      1) Segments images with ACE
      2) Convert raw tif/tiff files to nifti for registration
      3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
      4) Voxelizes high-resolution segmentation results into density maps with Allen atlas resolution
      5) Warps voxelied segmentation maps from native space to Allen atlas
      6) Generates group-wise heatmaps of cell density using the average of voxelized and warped segmentation maps in each group
      7) Computes group-level statistics/correlation using cluster-wise analysis on voxelized and warped segmentation maps

   single or multi method arguments:
      user is required to pass either single or multi method arguments

      -s SINGLE_TIFF_DIR, --single SINGLE_TIFF_DIR
                              path to single raw tif/tiff data folder
      -c CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE, --control CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE
                              FIRST: path to base control directory. SECOND: example
                              path to control subject tiff directory
      -t TREATED_BASE_DIR TREATED_TIFF_DIR_EXAMPLE, --treated TREATED_BASE_DIR TREATED_TIFF_DIR_EXAMPLE
                              FIRST: path to base treated directory. SECOND: example
                              path to treated subject tiff directory

   required arguments:
      (set the single or multi method arguments first)

      -sao SA_OUTPUT_FOLDER, --sa_output_folder SA_OUTPUT_FOLDER
                              path to output file folder
      -sam {unet,unetr,ensemble}, --sa_model_type {unet,unetr,ensemble}
                              model architecture
      -sar X-res Y-res Z-res, --sa_resolution X-res Y-res Z-res
                              voxel size (type: float)

   useful/important arguments:
      -sag SA_GPU_INDEX, --sa_gpu_index SA_GPU_INDEX
                              index of the GPU to use (type: int; default: 0)
      -ctnd CTN_DOWN, --ctn_down CTN_DOWN
                              Down-sample ratio for conversion (default: 5)
      -rcao RCA_ORIENT_CODE, --rca_orient_code RCA_ORIENT_CODE
                              to orient nifti from original orientation to
                              'standard/Allen' orientation, (default: ALS)
      -rcav {10,25,50}, --rca_voxel_size {10,25,50}
                              labels voxel size/Resolution in um (default: 10)
      -rvad RVA_DOWNSAMPLE, --rva_downsample RVA_DOWNSAMPLE
                              downsample ratio for voxelization, recommended: 5 <=
                              ratio <= 10 (default: 10)
      -rwcv {10,25,50}, --rwc_voxel_size {10,25,50}
                              voxel size/Resolution in um for warping (default: 25)
      --rerun-registration TRUE/FALSE
                              Whether to rerun registration step of flow; TRUE =>
                              Force re-run (default: false)
      --rerun-segmentation TRUE/FALSE
                              Whether to rerun segmentation step of flow; TRUE =>
                              Force re-run (default: false)
      --rerun-conversion TRUE/FALSE
                              Whether to rerun conversion step of flow; TRUE =>
                              Force re-run (default: false)

   --------------------------------------------------
   
   Use -hv or --help_verbose flag for more verbose help

.. note::

   There are a number of optional arguments including TFCE cluster-wise analysis parameters that can be provided to the
   respective function invoked by the workflow. These arguments have been 
   omitted here for readability but can be viewed by running ``miracl flow ace -hv``.

ACE Quick Start
---------------

The following arguments are the minimum required to run the ACE workflow:

Mode 1: Running ACE for two groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. table::

   ==================================  ================================================  ===================  ===================================================================================================
   Flag                                Parameter                                         Type                 Description                     
   ==================================  ================================================  ===================  ===================================================================================================
   \-c, \-\-control                    CONTROL_BASE_DIR, CONTROL_TIFF_DIR_EXAMPLE        ``(str, str)``       FIRST: path to base control directory; SECOND: example path to control subject tiff directory
   \-t, \-\-treated                    TREATED_BASE_DIR, TREATED_TIFF_DIR_EXAMPLE        ``(str, str)``       FIRST: path to base treated directory; SECOND: example path to treated subject tiff directory
   \-sam, \-\-sa_model_type            {unet,unetr,ensemble}                             ``str``              model architecture              
   \-sao, \-\-sa_output_folder         SA_OUTPUT_FOLDER                                  ``str``              path to output file folder
   \-sar, \-\-sa_resolution            X-res Y-res Z-res                                 ``(str, str, str)``  voxel size 
   ==================================  ================================================  ===================  ===================================================================================================

Mode 2: Running ACE for a single subject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. table::

   ==================================  ================================================  ===================  ===================================================================================================
   Flag                                Parameter                                         Type                 Description                     
   ==================================  ================================================  ===================  ===================================================================================================
   \-s, \-\-single                     SINGLE_TIFF_DIR                                   ``str``              path to single raw tif/tiff data folder
   \-sam, \-\-sa_model_type            {unet,unetr,ensemble}                             ``str``              model architecture              
   \-sao, \-\-sa_output_folder         SA_OUTPUT_FOLDER                                  ``str``              path to output file folder
   \-sar, \-\-sa_resolution            X-res Y-res Z-res                                 ``(str, str, str)``  voxel size 
   ==================================  ================================================  ===================  ===================================================================================================



Main outputs
============

.. code-block::

   seg_final # segmentation output including model(s) outputs and uncertainty estimates
   conv_final # conversion (tiff to nifti) output
   clar_allen_reg # registration output / preliminary files  
   reg_final  # main registration output 
   vox_final 
   warp_final
   
   # the following outputs are generated only in Mode 1
   heatmap_final
   cluster_final # cluster-wise analysis output including p_value and f_stats maps
   corr_final # correlation analysis output including correlation maps and p_value maps

.. _example_anchor:

Example of running ACE flow on multiple subjects (Mode 1):
==========================================================

.. code-block::

   $ miracl flow ace \
      -c ./non_walking/ ./non_walking/Newton_HC1/cells/ \
      -t ./walking/ ./walking/Newton_UI1/cells/ \
      -sao ./output_dir \
      -sam unet


Example of running ACE on single subject (Mode 2) (`link to sample data <https://drive.google.com/drive/folders/14xWysQshKxwuTDWEQHT3OGKcH16scrrQ>`__):
=======================================================================================================================================================

.. code-block::

   $ miracl flow ace \
      -s ./Ex_561_Em_600_stitched/ \
      -sao ./output_dir \
      -sam unet \
      -rcao ARI \
      -sar 3.5 3.5 4.0 \
      -ctnd 10 \ 
      -rcav 25 \
      --ctn_channame Signal

.. note::

   The user can also run the ACE segmentation module or the ACE cluster-wise analysis module separately.
   Examples of running these modules separately are provided below.

Example of running only ACE segmentation module on one single subject (`link to sample data <https://drive.google.com/drive/folders/14xWysQshKxwuTDWEQHT3OGKcH16scrrQ>`__):
=======================================================================================================================================================================================

.. code-block::

   $ miracl seg ace \
      -sai ./Ex_561_Em_600_stitched/ \
      -sao ./output_dir \
      -sam unetr


Example of running only ACE cluster wise analysis on voxelized and warped segmentation maps (`link to sample data <https://drive.google.com/drive/folders/1IgN9fDEVNeeT0a_BCzy3nReJWfxbrg72>`__):
=============================================================================================================================================================================================================

.. code-block::

   $ miracl stats ace \
      -c ./ctrl/ \
      -t ./treated/ \
      -sao ./output_dir \
      -rwcv 25

More information on the ``miracl stats ace`` function can be found
:doc:`here <../../stats/ace_cluster/ace_cluster>`.


.. |linktoworkshop| replace:: :doc:`here <../../../downloads/workshops/2024/stanford_20_03_2024/stanford_20_03_2024>`

.. include:: ../../../directives/tutorial_notebook_links.txt
