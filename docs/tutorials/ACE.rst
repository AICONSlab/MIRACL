ACE \*\*new feature\*\*
#######################

AI-based Cartography of Ensembles (ACE) segmentation method and workflow

.. note::
   The :program:`ACE Segmentation Function` and the :program:`ACE 
   Workflow` are currently in the final stages of testing and will 
   be available for download in version ``2.3.1`` which will be 
   released in **early January 2024**.

ACE Segmentation Function
=========================

:program:`ACE` can be found in :program:`MIRACL's` ``segmentation`` section.
To look at the arguments that need to be provided to the ``function``, invoke 
the help menu:

.. code-block::

   $ miracl seg ace -h

The following menu should be printed to the terminal:

.. code-block::

   usage: miracl ace [-h] -sai SA_INPUT_FOLDER -sao SA_OUTPUT_FOLDER -sam
                     {unet,unetr,ensemble} [-sas height width depth]
                     [-sar X-res Y-res Z-res] [-saw SA_NR_WORKERS]
                     [-sac SA_CACHE_RATE] [-sasw SA_SW_BATCH_SIZE] [-samc] [-sav]
                     [-sau]
   
   AI-based Cartography of Ensembles (ACE) segmentation method
   
   optional arguments:
     -h, --help            show this help message and exit
     -sai SA_INPUT_FOLDER, --sa_input_folder SA_INPUT_FOLDER
                           path to raw tif/tiff data folder
     -sao SA_OUTPUT_FOLDER, --sa_output_folder SA_OUTPUT_FOLDER
                           path to output file folder
     -sam {unet,unetr,ensemble}, --sa_model_type {unet,unetr,ensemble}
                           model architecture
     -sas height width depth, --sa_image_size height width depth
                           image size (type: int; default: fetched from image
                           header)
     -sar X-res Y-res Z-res, --sa_resolution X-res Y-res Z-res
                           voxel size (type: _validate_vox_res)
     -saw SA_NR_WORKERS, --sa_nr_workers SA_NR_WORKERS
                           number of cpu cores deployed to pre-process image
                           patches in parallel (type: int; default: 4)
     -sac SA_CACHE_RATE, --sa_cache_rate SA_CACHE_RATE
                           percentage of raw data that is loaded into cpu during
                           segmentation (type: float; default: 0.0)
     -sasw SA_SW_BATCH_SIZE, --sa_sw_batch_size SA_SW_BATCH_SIZE
                           number of image patches being processed by the model
                           in parallel on gpu (type: int; default: 4)
     -samc, --sa_monte_dropout
                           use Monte Carlo dropout (default: False)
     -sav, --sa_visualize_results
                           visualizing model output after predictions (default:
                           False)
     -sau, --sa_uncertainty_map
                           enable map (default: False)

.. table::

   ===============================  =====================  =========  =======================================================================================  =============================
   Flag                             Parameter              Type       Description                                                                              Default
   ===============================  =====================  =========  =======================================================================================  =============================
   \-sai, \-\-sa_input_folder       SA_INPUT_FOLDER        ``str``    path to raw tif/tiff data folder                                                         ``None`` (required)
   \-sao, \-\-sa_output_folder      SA_OUTPUT_FOLDER       ``str``    path to output file folder                                                               ``None`` (required)
   \-sam, \-\-sa_model_type         {unet,unetr,ensemble}  ``str``    model architecture                                                                       ``None`` (required)
   \-sas, \-\-sa_image_size         height width depth     ``int``    image size; provided as three arguments                                                  ``fetched from image header``
   \-sar, \-\-sa_resolution         X-res Y-res Z-res      ``int``    voxel resolution; provided as three arguments                                            ``None`` (required)
   \-saw, \-\-sa_nr_workers         SA_NR_WORKERS          ``int``    number of cpu cores deployed to pre-process image patches in parallel                    ``4``
   \-sac, \-\-sa_cache_rate         SA_CACHE_RATE          ``float``  percentage of raw data that is loaded into cpu during segmentation                       ``0.0``
   \-sasw,\ \--sa_sw_batch_size     SA_SW_BATCH_SIZE       ``int``    number of image patches being processed by the model in parallel on gpu                  ``4``
   \-samc,\ \--sa_monte_dropout     True/False             ``bool``   use Monte Carlo dropout                                                                  ``False``
   \-sav, \-\-sa_visualize_results  True/False             ``bool``   visualizing model output after predictions                                               ``False``
   \-sau, \-\-sa_uncertainty_map    True/False             ``bool``   enable map                                                                               ``False``
   ===============================  =====================  =========  =======================================================================================  =============================

.. note::
   The ``\-sa`` in the flag part stands for ``segmentation ACE``.




   
