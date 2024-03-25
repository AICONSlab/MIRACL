ACE Workflow
############

**A**\ I-based **C**\ artography of **E**\ nsembles (**ACE**) pipeline highlights:

1. Cutting-edge vision transformer and CNN-based DL architectures trained on 
   very large LSFM datasets (`link to sample data <https://drive.google.com/drive/folders/14xWysQshKxwuTDWEQHT3OGKcH16scrrQ>`__
   and :ref:`refer to example section<example_anchor>`) to map brain-wide neuronal activity.
2. Optimized cluster-wise statistical analysis with a threshold-free 
   enhancement approach to chart subpopulation-specific effects at the laminar 
   and local level, without restricting the analysis to atlas-defined regions 
   (`link to sample data <https://drive.google.com/drive/folders/1IgN9fDEVNeeT0a_BCzy3nReJWfxbrg72>`__ 
   and :ref:`refer to example section<example_anchor>`).
3. Modules for providing DL model uncertainty estimates and fine-tuning.
4. Interface with MIRACL registration to create study-specific atlases.
5. Ability to account for covariates at the cluster level and map the 
   connectivity between clusters of activations.

Main Inputs
============

Control and Treated directories, containing whole-brain 3D LSFM datasets for multiple subjects.
OR 
A single directory containing a single subject's whole-brain 3D LSFM dataset.

CLI
===

To get more information about the workflow and its required arguments 
use the following command on the cli:

.. code-block::

   $ miracl flow ace -h

The following information will be printed to the terminal:

.. code-block::

   usage: miracl ace (-s SINGLE_TIFF_DIR | 
                     (-c CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE -e EXPERIMENT_BASE_DIR EXPERIMENT_TIFF_DIR_EXAMPLE))
                     -sao SA_OUTPUT_FOLDER -sam {unet,unetr,ensemble}
                     (--overwrite | --no-overwrite)

     1) Segments images with ACE
     2) Registers tissue cleared data (down-sampled nifti images) to Allen Reference mouse brain atlas
     3) Voxelizes high-resolution segmentation maps to downsample into Allen atlas resolution
     4) Warps voxelied segmentation maps from native space to Allen atlas
     5) Generates group-wise heatmaps of cell density using the average of voxelized and warped segmentation maps in each group
     6) Computes group-level statistics/correlation using cluster-wise analysis on voxelized and warped segmentation maps
   
   Single or multi method arguments:
   -s SINGLE_TIFF_DIR, --single SINGLE_TIFF_DIR
                           path to single raw tif/tiff data folder
   -c CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE, --control CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE
                           FIRST: path to base control directory. SECOND: example
                           path to control subject tiff directory
   -e EXPERIMENT_BASE_DIR EXPERIMENT_TIFF_DIR_EXAMPLE, --experiment EXPERIMENT_BASE_DIR EXPERIMENT_TIFF_DIR_EXAMPLE
                           FIRST: path to base experiment directory. SECOND:
                           example path to experiment subject tiff directory
   --overwrite           overwrite existing output files for comparison
                           workflow
   --no-overwrite        do not overwrite existing output files for comparison
                           workflow. This flag can be used to run only the stats
                           analysis (if the subject-only steps have already been
                           run).

   required arguments:
   -sao SA_OUTPUT_FOLDER, --sa_output_folder SA_OUTPUT_FOLDER
                           path to output file folder
   -sam {unet,unetr,ensemble}, --sa_model_type {unet,unetr,ensemble}
                           model architecture

   utility arguments:
   -ua U_ATLAS_DIR, --u_atlas_dir U_ATLAS_DIR
                           path of atlas directory (default:
                           '/code/atlases/ara/')

   --------------------------------------------------

   Use -hv or --help_verbose flag for more verbose help and view other ACE modules arguments


.. note::

   There are a number of optional arguments including TFCE cluster-wise analysis parameters that can be provided to the
   respective function invoked by the workflow. These arguments have been 
   ommitted here for readability but can be viewed by running ``miracl flow ace -hv``.

.. table::

   ==================================  ================================================  ==============  ====================================================================================
   Flag                                Parameter                                         Type            Description                     
   ==================================  ================================================  ==============  ====================================================================================
   \-s, \-\-single                     SINGLE_TIFF_DIR                                   ``str``         path to raw tif/tiff data folder
   \-c, \-\-control                    CONTROL_BASE_DIR, CONTROL_TIFF_DIR_EXAMPLE        ``(str, str)``  path to base control directory, example path to control subject tiff directory
   \-e, \-\-experiment                 EXPERIMENT_BASE_DIR, EXPERIMENT_TIFF_DIR_EXAMPLE  ``(str, str)``  path to base experiment directory, example path to experiment subject tiff directory
   \-sam, \-\-sa_model_type            {unet,unetr,ensemble}                             ``str``         model architecture              
   \-\-overwrite \| \-\-no\-overwrite                                                    ``bool``        whether to overwrite existing output files for comparison workflow  
   ==================================  ================================================  ==============  ====================================================================================

Main outputs
============

.. code-block::

   clar_allen_reg # registration output / pre-liminary files  
   conv_final # conversion (tiff to nifti) output
   reg_final  # main registration output 
   seg_final # segmentation output including model(s) outputs and uncertainty estimates
   vox_final 
   warp_final 
   heatmap_final
   cluster_final # cluster-wise analysis output including p_value and f_stats maps
   corr_final # correlation analysis output including correlation maps and p_value maps

Executes:

.. code-block::

   seg/ace_interface.py
   conv/miracl_conv_convertTIFFtoNII.py
   reg/miracl_reg_clar-allen.sh
   seg/miracl_seg_voxelize_parallel.py
   reg/miracl_reg_warp_clar_data_to_allen.sh
   stats/miracl_stats_heatmap_group.py
   stats/miracl_stats_ace_interface.py

.. _example_anchor:

Example of running ACE on single subject (segmenation + registration + voxelization + warping) (`link to sample data <https://drive.google.com/drive/folders/14xWysQshKxwuTDWEQHT3OGKcH16scrrQ>`__):
====================================================================================================================================================================================================

.. code-block::

   $ miracl flow ace \
      -s ./non_walking/Newton_HC1/cells/ \
      -sao ./output_dir \
      -sam unet \
      --overwrite


Example of running ACE flow on multiple subjects:
=================================================

.. code-block::

   $ miracl flow ace \
      -c ./non_walking/ ./non_walking/Newton_HC1/cells/ \
      -e ./walking/ ./walking/Newton_UI1/cells/ \
      -sao ./output_dir \
      -sam unet \
      --overwrite


Example of running only ACE segmentation module on one single subject (`link to sample data <https://drive.google.com/drive/folders/14xWysQshKxwuTDWEQHT3OGKcH16scrrQ>`__):
======================================================================================================================================================================================

.. code-block::

   $ miracl seg ace \
      -sai ./Ex_561_Em_600_stitched/ \
      -sao ./output_dir \
      -sam unetr


Example of running only ACE cluster wise analysis on voxelized and warped segmentation maps (`link to sample data <https://drive.google.com/drive/folders/1IgN9fDEVNeeT0a_BCzy3nReJWfxbrg72>`__):
============================================================================================================================================================================================================

.. code-block::

   $ miracl stats ace \
      -c ./ctrl/ \
      -e ./treated/ \
      -sao ./output_dir \
