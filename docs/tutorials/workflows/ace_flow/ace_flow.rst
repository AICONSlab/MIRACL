ACE Workflow
############

**A**\ I-based **C**\ artography of **E**\ nsembles (**ACE**) pipeline highlights:

1. Cutting-edge vision transformer and CNN-based DL architectures trained on 
   very large LSFM datasets (:ref:`refer to example section<example_anchor>`) 
   to map brain-wide local/laminar neuronal activity.
2. Optimized cluster-wise statistical analysis with a threshold-free 
   enhancement approach to chart subpopulation-specific effects at the laminar 
   and local level, without restricting the analysis to atlas-defined regions 
   (:ref:`refer to example section<example_anchor>`).
3. Modules for providing DL model uncertainty estimates and fine-tuning.
4. Interface with MIRACL registration.
5. Ability to map the connectivity between clusters of activations.

Installation
============

To install the ACE workflow, refer to the MIRACL installation guide:

- :doc:`Installation guide <../../../installation/installation>`

.. note::

   Make sure that you set the GPU option during installation.
   Once the installation is complete, enter the ``docker`` container using ``docker exec -it <CONTAINER_NAME> bash``
   and run the ``nvidia-smi`` command to ensure your GPU is detected.

As of MIRACL version `2.4.2` the pre-trained DL models are publicly available and will have automatically been downloaded when you installed MIRACL.

.. _model_directory_specification:

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

.. note::
   By default, the installation script mounts the ``<WHERE YOU CLONED MIRACL>/miracl/``
   directory to the docker container at ``/code/miracl/``. Thus, copying the model
   files to the right location **outside** the docker container will make them
   available inside the container.

Video Tutorial
==============

`Video tutorial <https://www.youtube.com/playlist?list=PLZeAd6YsEkyhWsHuym5dTV2wjQ299ekm8>`_

- This video tutorial covers the following topics:
   - MIRACL installation validation
   - Download sample data
   - Run ACE on a single subject (Mode 2) including deep learning
     segmentation of cFos+ cells, registration, voxelization, and warping
   - Analyze the results of the above step
   - Run ACE cluster-wise statistical algorithm between two groups to map
     local cell activation
   - Analyze the results of the above step

.. TODO: update the tutorial link


Main Inputs
============

Mode 1: Running ACE for two groups
- Control and Treated directories, containing whole-brain 3D LSFM datasets for multiple subjects.

OR

Mode 2: Running ACE for a single subject
- A single directory containing a single subject's whole-brain 3D LSFM dataset.

.. note::

   The trained DL models are not considered inputs, but are required to
   run ACE. 

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
        [--rerun-instance-segmentation TRUE/FALSE]
        [--rerun-conversion TRUE/FALSE]
        [--no-instance-segmentation]
        [--no-validate-clusters]

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
                              whether to rerun registration step of flow; TRUE =>
                              Force re-run (default: false)
      --rerun-segmentation TRUE/FALSE
                              whether to rerun segmentation step of flow; TRUE =>
                              Force re-run (default: false)
      --rerun-instance-segmentation TRUE/FALSE
                              whether to rerun instance segmentation step of flow;
                              TRUE => Force re-run (default: false)
      --rerun-conversion TRUE/FALSE
                              whether to rerun conversion step of flow; TRUE =>
                              Force re-run (default: false)
      --no-instance-segmentation
                              Do not run instance segmentation (default: False).
                              Instance seg is used to identify and label neurons in
                              the image. It is useful for counting and downstream
                              tasks.
      --no-validate-clusters
                              Do not validate clusters (default: False). Validate
                              clusters is used to get native space statistics for
                              each subject based on the ouput of ACE TFCE stats.

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

   final_ctn_down_<CONVERSION DOWNSAMPLE RATIO>_rca_voxel_size_<REGISTRATION VOXEL SIZE>/ # main output folder
   |-- seg_final/
      |-- ...
      |-- generated_patches/
         |-- cc_patches/
            |-- neuron_info_final.json
            |-- ...
      |-- cc_slices/
         |-- ...
   |-- conv_final/
      |-- <CONVERSION NAME>.nii.gz
   |-- clar_allen_reg/
      |-- ...
   |-- reg_final/
      |-- annotation_*_tiff_clar/
      |-- annotation_*_clar_space_downsample.nii.gz
      |-- annotation_*_clar_downsample.nii.gz
      |-- clar_downsample*.nii.gz
   |-- vox_final/
      |-- voxelized_seg_seg.nii.gz
   |-- warp_final/
      |-- voxelized_seg_seg_allen_space.nii.gz
   
   # the following outputs are generated only in Mode 1
   |-- heatmap_final/
      |-- group_1_mean_plot.tiff
      |-- group_2_mean_plot.tiff
      |-- group_difference_mean_plot.tiff
   |-- clust_final/
      |-- f_obs.nii.gz
      |-- p_values.nii.gz
      |-- pvalue_heatmap_mean_plot.tiff
   |-- corr_final/
   |-- neuron_info_json/
      |-- ...
   |-- validate_clusters_final/
      |-- sig_clusters_summary.csv

- ``seg_final``: Contains the segmentation output (binary) including model(s) outputs (and
  uncertainty estimates) in slice format that match with the raw data naming.
  ``generated_patches/`` contains the 3D binary segmentation output (and model uncertainty estimates).
  It also contains the 3D instance segmentation output in the ``cc_patches/`` directory paired
  with the neuron info dictionary. Lastly the ``cc_slices/`` directory contains instance segmentation 
  output in slice format in the  with the raw data naming.
- ``conv_final``: Contains the conversion (tiff to nifti) output. The name of this file depends
  on the parameters used in conversion. This will be the only file in this directory.
- ``clar_allen_reg``: Contains the registration outputs / preliminary files.
- ``reg_final``: Contains the main registration outputs.

   - ``annotation_*_tiff_clar``: Contains the atlas annotations in native space.
     These are saved in slice format, with the same naming as the raw input
   - ``annotation_*_clar_space_downsample.nii.gz``: Contains the atlas annotations
     in native space in nifti format. Can be overlaid on the conversion output.
   - ``annotation_*_clar_downsample.nii.gz``: Contains the atlas annotations in
     atlas space in nifti format. Can be overlaid on ``clar_downsample*.nii.gz``.
   - ``clar_downsample*.nii.gz``: Contains the downsampled conversion output 
     warped to atlas space.

.. note::

   The ``annotation_*_clar_downsample.nii.gz`` file is the most important file in this directory.
   Please overlay this file on the ``clar_downsample*.nii.gz`` file to visualize and check the
   registration output in native space and make sure it is correct.

- ``vox_final``: Contains the voxelized segmentation output.
- ``warp_final``: Contains the voxelized + warped segmentation output. This file
  is in atlas space.
- ``heatmap_final``: Contains the group-wise heatmaps of cell density using the average
  of voxelized and warped segmentation maps in each group. Also contains the group difference
  heatmap. ``group_1_mean_plot.tiff`` is for the control group, ``group_2_mean_plot.tiff``
  is for the treated group.
- ``clust_final``: Contains the cluster-wise TFCE permutation statistics at the atlas space
  (``f_obs.nii.gz``), the p-value image of the F-statistics (``p_values.nii.gz``), and the p-value heatmap
  projected onto the Allen atlas space (``pvalue_heatmap_mean_plot.tiff``). All p-values are expressed
  as ``-log10(p-value)``.
- ``corr_final``: Contains the correlation analysis output including correlation maps and p_value maps.
- ``neuron_info_json``: Contains the neuron info dictionary of each subject in json format.
  This is used to place all dictionaries in a central directory for easier use by the workflow.
- ``validate_clusters_final``: Contains pre-processed nifti p-value cluster files in atlas space and
  a summary of the properties of the significant clusters in CSV format, including the 
  number of neurons for each subject in native space.



.. _example_anchor:

Examples
========

Example of running ACE flow on multiple subjects (Mode 1):
----------------------------------------------------------

.. code-block::

   $ miracl flow ace \
      --control ./non_walking/ ./non_walking/Newton_HC1/cells/ \
      --treated ./walking/ ./walking/Newton_UI1/cells/ \
      --sa_output_folder ./output_dir \
      --sa_model_type unet \
      --sa_resolution 1.4 1.4 5.0


Example of running ACE on single subject (Mode 2: Segmentation & Registration): 
-------------------------------------------------------------------------------

.. note::

   You must download the sample data before running the below command.
   To do so, run:

   .. code-block::

      $ docker exec -it <CONTAINER_NAME> bash
      $ cd <WHERE YOU WANT TO DOWNLOAD DATA>
      $ download_sample_data

   This will open an interface where you can select which data
   you want to download. For this tutorial, you will need to
   download option ``1``.

   Alternatively, download mode 2 sample data `here <https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/sample_data/ace/ace_sample_data_mode_2.zip>`__.

.. code-block::

   $ miracl flow ace \
      --single ./Ex_561_Em_600_stitched/ \
      --sa_output_folder ./output_dir \
      --sa_model_type unet \
      --rca_orient_code ARI \
      --sa_resolution 3.5 3.5 4.0 \
      --ctn_down 10 \ 
      --rca_voxel_size 25 \
      --ctn_channame Signal \
      --sa_batch_size 2

.. tip::

   Here we use a batch size of 2 for the DL model so that it fits in the GPU memory.
   The batch size can be adjusted based on the GPU memory available on the current system.
   Experienced users can try increasing the batch size to speed up the processing time.

.. note::

   The user can also run the ACE segmentation module or the ACE cluster-wise analysis module separately.
   Examples of running these modules separately are provided below.

Example of running ACE on one single subject (Mode 2: Segmentation Only):
-------------------------------------------------------------------------

.. note::

   You must download the sample data before running the below command.
   To do so, run:

   .. code-block::

      $ docker exec -it <CONTAINER_NAME> bash
      $ cd <WHERE YOU WANT TO DOWNLOAD DATA>
      $ download_sample_data

   This will open an interface where you can select which data
   you want to download. For this tutorial, you will need to
   download option ``1``.

   Alternatively, download mode 2 sample data `here <https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/sample_data/ace/ace_sample_data_mode_2.zip>`__.

.. code-block::

   $ miracl seg ace \
      --single ./Ex_561_Em_600_stitched/ \
      --sa_output_folder ./output_dir \
      --sa_model_type unetr \
      --sa_batch_size 2


Example of running only ACE cluster wise analysis on voxelized and warped segmentation maps:
--------------------------------------------------------------------------------------------

.. note::

   You must download the sample data before running the below command.
   To do so, run:

   .. code-block::

      $ docker exec -it <CONTAINER_NAME> bash
      $ cd <WHERE YOU WANT TO DOWNLOAD DATA>
      $ download_sample_data

   This will open an interface where you can select which data
   you want to download. For this tutorial, you will need to
   download option ``2``.

   Alternatively, download stats sample data `here <https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/sample_data/ace/ace_sample_data_stats.zip>`_.

.. code-block::

   $ miracl stats ace \
      --control ./ctrl/ \
      --treated ./treated/ \
      --sa_output_folder ./output_dir \
      --rwc_voxel_size 25

More information on the ``miracl stats ace`` function can be found
:doc:`here <../../stats/ace_cluster/ace_cluster>`.


.. |linktoworkshop| replace:: :doc:`here <../../../downloads/workshops/2024/stanford_20_03_2024/stanford_20_03_2024>`

.. include:: ../../../directives/tutorial_notebook_links.txt


ACE Fine-Tuning
===============

ACE can be used with lightsheet microscopy datasets from other cellular 
markers with different morphological features compared to c-Fos 
(which ACE models were trained on) by fine-tuning the 
pre-trained model(s). To fine-tune ACE, you need:

1. A directory of 3D training images in tiff format.
2. A directory of 3D training binary ground-truth images in tiff format.
3. A directory of 3D validation images in tiff format.
4. A directory of 3D validation binary ground-truth images in tiff format.
5. Access to a GPU and a pre-trained model.

.. note::

   The images (both train and validation) and ground-truth labels must have
   a size of at least 128x128x128 voxels.


To fine-tune the model, you can use the following command:

.. code-block::

   $ miracl seg ace_finetune \
      --train-images ./train_dir/ \
      --train-labels ./train_gt_dir/ \
      --val-images ./val_dir/ \
      --val-labels ./val_gt_dir/ \
      --output ./output_dir/ \
      --config /code/miracl/seg/ace_finetune_model_config.yml

The ``ace_finetune_model_config.yml`` file contains the model architecture 
and hyperparameters for the fine-tuning process.

.. note::

   Please do not change the sections of the config file labelled
   ``unet:`` and ``unetr:``. These sections contain the model architecture.
   If a user is changing the model architecture, this is no longer considered
   fine-tuning. Further, the script will raise an error since the user 
   is trying to load in model weights for a different model architecture.

The script will output the fine-tuned model weights in the output directory. The
user can then :ref:`use this model to run the ACE workflow above<model_directory_specification>`.

