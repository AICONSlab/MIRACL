MAPL3 Workflow
##############

Summary and key highlights
==========================

**M**\ apping **A**\ xonal **P**\ rojections in **L**\ ight-sheet Fluorescence Microscopy in **3**\ D (:program:`MAPL3`) is an end-to-end deep learning pipeline for generalizable, brain-wide mapping of structural connectivity at the single-axon level using tera-voxel light sheet fluorescence microscopy (LSFM) dataset. It's built for scalability, precision, and biological insight and bridges the gap between raw LSFM data and interpretable brain-wide connectivity maps.

- **Hybrid CNN–Transformer Architecture**: A novel deep learning design that fuses convolutional precision with transformer-level context awareness, capturing both fine axonal details and global anatomical structure.
- **Self-Supervised Generative Pretraining**: Pretrained on 22,000+ 3D sub-volumes using advanced self-supervised learning (SSL) and unique patch-based augmentation strategies. Enhances model robustness across diverse imaging conditions and experimental setups.
- **State-of-the-Art Performance**: Extensively benchmarked against leading DL pipelines, :program:`MAPL3` consistently outperforms them in both in- and out-of-distribution datasets, from patch-level inference to full-brain reconstructions.
- **Neuroscientific Discovery at Scale**: :program:`MAPL3` reveals cell-type-specific axonal connectivity patterns previously unresolved by existing methods, enabling new insights into mesoscale and quantitative brain circuitry analysis.

Installation
============

To install the :program:`MAPL3` workflow, refer to the MIRACL installation guide:

- :doc:`Installation guide <../../../installation/installation>`

.. _model_directory_specification:

.. attention::
   
   :program:`MAPL3` has not yet officially been released but will be available in the 
   next release of :program:`MIRACL`.

   The :program:`MAPL3` workflow can only be run with the pre-trained DL model. To get 
   access to the model please reach out to `a.attarpour@mail.utoronto.ca <mailto:a.attarpour@mail.utoronto.ca>`_.

   The model will be included by default in a future release once :program:`MAPL3` 
   has been published.

.. note::
   
   The DL models must be in a specific directory structure to be used by the MAPL3 workflow.

   Once you have the models, place them in the required directory structure by using the following commands:

   .. code-block::

      cp <PATH TO THE DOWNLOADED MODEL FILE> <WHERE YOU CLONED MIRACL>/miracl/seg/mapl3/models/best_metric_model.pth

   The path <WHERE YOU CLONED MIRACL> is the path where you cloned the MIRACL repository. This is the
   location where you ran these :ref:`installation steps <git clone target>`.

   To check that the models are in the correct directory structure, run the following commands:

   .. code-block::

      ls <WHERE YOU CLONED MIRACL>/miracl/seg/mapl3/models/unet/best_metric_model.pth

   The output should be the following:

   .. code-block::

      best_metric_model.pth

   By default, the installation script mounts the ``<WHERE YOU CLONED MIRACL>/miracl/``
   directory to the docker container at ``/code/miracl/``. Thus, copying the model
   files to the correct location **outside** the docker container (i.e. on the host 
   system) will make them available inside the container.

Command Line Interface (CLI) Usage
==================================

To use the :program:`MAPL3` on the CLI, you must first enter the docker container by running the 
following command from the CLI:

.. code-block::

   $ docker exec -it <YOUR CONTAINER NAME> bash

Once in the container, you can get more information about the workflow and its required 
arguments using:

.. code-block::

   $ miracl flow mapl3 -h

This will print a comprehensive overview of all arguments that can be passed to the 
:program:`MAPL3` workflow.

Main Inputs
-----------

Most arguments have sensible default values and will not have to be provided by the user
manually. However, the :program:`MAPL3` workflow always requires the following arguments:

.. table::

   ==============================================  =======  ==========================================================================
   Flag                                            Type     Description
   ==============================================  =======  ==========================================================================
   \-mwfc_ratf, \-\-mwfc_raw_autoflor_tiff_folder  ``str``  RAW Tiff folder object i.e. path to the folder with autoflor Tiffs in it
   \-mwfc_rstf, \-\-mwfc_raw_signal_tiff_folder    ``str``  RAW Tiff folder object i.e. path to the folder with signal Tiffs in it
   \-mwfc_cof, \-\-mwfc_results_folder             ``str``  Path to MAPL3 workflow output folder i.e. where your results will be saved
   ==============================================  =======  ==========================================================================

Commonly Useful Args
--------------------

The following table presents an overview of the arguments commonly changed from the 
defaults by the user:

.. table::

   ================  ==============================================  ===========  ==========  ==============================================================================================================================
   Module            Flag                                            Type         Default     Description
   ================  ==============================================  ===========  ==========  ==============================================================================================================================
   Conversion        \-mctn_d, \-\-mctn_down                         ``int``      ``5``       Down-sample ratio for conversion
   Conversion        \-mctn_vx, \-\-mctn_resx                        ``float``    ``5``       Original resolution in x-y plane in um
   Conversion        \-mctn_vz, \-\-mctn_resz                        ``float``    ``5``       Original thickness (z-axis resolution / spacing between slices) in um
   Registration      \-mrca_o, \-\-mrca_orient_code                  ``str``      ``ALS``     Orient nifti from original orientation to 'standard/Allen' orientation
   Patch generation  \-mgp_e, \-\-mgp_brain_mask_erosion_flag        ``bool``     ``False``   Set if you want to erode the brain mask
   Preprocessing     \-mpp_tpt, \-\-mpp_tissue_percentage_threshold  ``float``    ``None``    Threshold between 0-100 to filter empty patches (required if metadata is provided)
   Preprocessing     \-mpp_it, \-\-mpp_intensity_threshold           ``float``    ``None``    Threshold between 0-100 (percent of int16: around 65K) to filter the patches whose 95 percentile of intensity falls below this
   Inference         \-mi_g, \-\-mi_gpu_index                        ``int/str``  ``0``       GPU index to be used; if you wanna use all the available gpus, pass 'all' as the flag argument
   Inference         \-mi_s, \-\-mi_save_prob_map_flag               ``bool``     ``False``   Set to save prob map
   Patch stacking    \-mps_d, \-\-mps_dtype                          ``str``      ``uint16``  Output data type (e.g., uint16, bool)
   Voxelization      \-mv_vx, \-\-mv_res_xy                          ``float``    ``1.0``     Resolution of the input in x and y in um
   Voxelization      \-mv_vz, --mv_res_z                             ``float``    ``1.0``     Resolution of the input in z in um
   Voxelization      \-mv_dx, --mv_downsample_yx_axis                ``int``      ``10``      Downsample ration for y and x axis
   Voxelization      \-mv_dz, --mv_downsample_z_axis                 ``int``      ``10``      Downsample ration for z axis
   ================  ==============================================  ===========  ==========  ==============================================================================================================================

Skipping Modules
----------------

The :program:`MAPL3` workflow also gives the user the option to skip modules. This is 
useful if a module fails later in the workflow but the user does not want to re-run the 
modules that have already finished succesfully. For example, to skip 
:program:`conversion` and :program:`registration`, the following flags can be passed 
and set to ``True``:

.. code-block::

   $ miracl flow mapl3 [OTHER_FLAGS] --skip_conversion True --skip_registration True

.. important::

   When using the skip flags it is important to provide all flags that where previously
   used for the modules that are being skipped i.e. your original command. This is in 
   case some of the arguments used for the skipped modules are being re-used in later 
   modules. E.g., skipping the registration module, if an orientation code was used 
   for the registration that was different from the default, it needs to be provided 
   together with the skip flags.

Output directories
------------------

The following folders will be generated by the workflow in the output folder:

.. code-block::

   clar_allen_reg/  
   extracted_features/  
   heatmaps/   
   normalized_raw_data/     
   reg_final/     
   stacked_patches/          
   voxelized_skeletonization/
   conv_final/      
   generated_patches/   
   inference/  
   preprocessing_parallel/  
   skeletonized/  
   voxelized_normalization/  
   warped_results/

Example workflow
================

A typical LSFM analysis could look like this:

.. code-block::

   $ miracl flow mapl3 \
     --mwfc_raw_autoflor_tiff_folder /data/Brain2/Ex_647_Em_680_stitched \
     --mwfc_raw_signal_tiff_folder /data/Brain2/Ex_488_Em_525_stitched \
     --mwfc_results_folder /data/projects/user/mapl3/run_1 \
     -mctn_vx 1.8 \
     -mctn_vz 3 \
     -mctn_d 20 \
     --mrca_orient_code PLI \
     --mgp_brain_mask_erosion_flag True \
     --mpp_intensity_threshold 1 \
     --mpp_tissue_percentage_threshold 20 \
     --mi_gpu_index all \
     --mi_save_prob_map True \
     --mps_dtype float32 \
     --mv_res_xy 1.8 \
     --mv_res_z 3 \
     --mv_downsample_yx_axis 10 \
     --mv_downsample_z_axis 6 \
     --skip_conversion True

In this example the user first provides the required flags for the folders containing 
the RAW autofluorescent and signal channel Tiff stacks as well as the output directory.
The conversion is run with a x/y voxel resolution of ``1.8`` and z resolution of ``3``
with a downsample factor of ``20``. For the registration a ``PLI`` code is used for the 
orientation and the brain mask is being eroded during patch generation. Thresholds are 
set for tissue percentage and intensity for the preprocessing module. All available 
GPU's are used and the probability map is saved during inference. ``float32`` is used 
as the output data type for patch stacking and the voxelization is using custom input 
resolutions and downsample rations for all axes. Lastly, the :program:`conversion` 
module is skipped by setting the ``--skip_conversion`` flag to ``True`` which means 
that the nifti file required for the :program:`registration` module is already present 
in the ``conv_final`` folder in the output directory.
