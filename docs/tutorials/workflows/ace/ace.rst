ACE Workflow
############

:program:`ACE` stands for **A**\ I-based **C**\ artography of **E**\ nsembles
(**ACE**) segmentation method and workflow. Some of its highlights are:

1. Cutting edge vision transformer and CNN-based DL architectures trained on 
   very large LSFM datasets to map cFos brain-wide
2. Interfaces to MIRACL registration algorithms to warp segmentation maps to a 
   study-specific atlas
3. Optimized cluster-wise statistical analysis with a threshold-free 
   enhancement approach to document and chart clusters of activation and their 
   associations at the laminar and local level

.. note::

   The :program:`ACE Segmentation Function` and the :program:`ACE 
   Workflow` are currently in the final stages of testing and will 
   be available for download in version ``2.3.1`` which will be 
   released in **early January 2024**.

ACE Workflow
============

.. note::

   :program:`ACE's` workflow is currently only available on the command line. 
   We are currently working on the GUI integration which will be integrated
   in **early 2024**.

Main outputs:

.. code-block::

   clar_allen_reg
   conv_final
   reg_final
   seg_final
   vox_final
   warp_final
   heatmap_final
   cluster_final

Executes:

.. code-block::

   seg/ace_interface.py
   conv/miracl_conv_convertTIFFtoNII.py
   reg/miracl_reg_clar-allen.sh
   seg/miracl_seg_voxelize_parallel.py
   reg/miracl_reg_warp_clar_data_to_allen.sh
   stats/miracl_stats_heatmap_group.py
   stats/miracl_workflow_ace_stats.py
   stats/miracl_summarize_clusters_corr.py

The :program:`ACE workflow` can be found in :program:`MIRACL's` ``flow`` 
section. To get more information about the workflow and its required arguments 
use the following command on the cli:

.. code-block::

   $ miracl flow ace -h

The following information will be printed to the terminal:

.. code-block::

   usage: miracl flow ace -sai input_folder -sao output_folder -sam model_type 
          -pcsw wild_type_dir -pcsd disease_group_dir -pcso output_directory

     1) Segments images with ACE
     2) Convert raw tif/tiff files to nifti for registration
     3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
     4) Voxelizes segmentation results into density maps with Allen atlas resolution
     5) Warps downsampled CLARITY data/channels from native space to Allen atlas

   required arguments:
     -sai SA_INPUT_FOLDER, --sa_input_folder SA_INPUT_FOLDER
                           path to raw tif/tiff data folder
     -sao SA_OUTPUT_FOLDER, --sa_output_folder SA_OUTPUT_FOLDER
                           path to output file folder
     -sam {unet,unetr,ensemble}, --sa_model_type {unet,unetr,ensemble}
                           model architecture
     -pcsw PCS_WILD_TYPE, --pcs_wild_type PCS_WILD_TYPE
                           wild type group directory (should contain warped
                           voxelized nifti files)
     -pcsd PCS_DISEASE, --pcs_disease PCS_DISEASE
                           disease group directory (should contain warped
                           voxelized nifti files)
     -pcso PCS_OUTPUT, --pcs_output PCS_OUTPUT
                           path of output directory

.. note::

   There are a number of optional arguments that can be provided to the
   respective function invoked by the workflow. These arguments have been 
   ommitted here for readability but will be printed when actually using 
   :program:`MIRACL`.

.. table::

   ===========================  =====================  =======  ================================
   Flag                         Parameter              Type     Description                     
   ===========================  =====================  =======  ================================
   \-sai, \-\-sa_input_folder   SA_INPUT_FOLDER        ``str``  path to raw tif/tiff data folder
   \-sao, \-\-sa_output_folder  SA_OUTPUT_FOLDER       ``str``  path to output file folder      
   \-sam, \-\-sa_model_type     {unet,unetr,ensemble}  ``str``  model architecture              
   \-pcsw, \-\-pcs_wild_type    PCS_WILD_TYPE          ``str``  wild type group directory
   \-pcsd, \-\-pcs_disease      PCS_DISEASE            ``str``  disease group directory
   \-pcso, \-\-pcs_output       PCS_OUTPUT             ``str``  path of output directory
   ===========================  =====================  =======  ================================
