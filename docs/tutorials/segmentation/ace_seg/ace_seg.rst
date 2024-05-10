ACE Segmentation Function
#########################

Cutting edge vision transformer and CNN-based DL architectures trained on very 
large LSFM datasets to map cFos brain-wide.

CLI
===

To look at the arguments that need to be provided to the function, invoke the 
help menu using:

.. code-block::

   $ miracl seg ace -h

The following menu will be printed to the terminal:

.. code-block::

   AI-based Cartography of Ensembles (ACE) segmentation method
   usage: miracl ace [-h]
                     -sai SINGLE
                     -sao SA_OUTPUT_FOLDER
                     -sam {unet,unetr,ensemble}
                     [-sas height width depth]
                     [-sar X-res Y-res Z-res]
                     [-saw SA_NR_WORKERS]
                     [-sac SA_CACHE_RATE]
                     [-sab SA_BATCH_SIZE]
                     [-samc SA_MONTE_CARLO]
                     [-sav] 
                     [-sau] 
                     [-sag SA_GPU_INDEX]
                     [-sat SA_BINARIZATION_THRESHOLD]
                     [-sap SA_PERCENTAGE_BRAIN_PATCH_SKIP]

   AI-based Cartography of Ensembles (ACE) segmentation method
     
   optional arguments:
       -h, --help            show this help message and exit
       -sai SINGLE, --single SINGLE
                             path to raw tif/tiff data folder
       -sao SA_OUTPUT_FOLDER, --sa_output_folder SA_OUTPUT_FOLDER
                             path to output file folder
       -sam {unet,unetr,ensemble}, --sa_model_type {unet,unetr,ensemble}
                             model architecture
       -sas height width depth, --sa_image_size height width depth
                             image size (type: int; default: fetched from image
                             header)
       -sar X-res Y-res Z-res, --sa_resolution X-res Y-res Z-res
                             voxel size (type: float)
       -saw SA_NR_WORKERS, --sa_nr_workers SA_NR_WORKERS
                             number of cpu cores deployed to pre-process image
                             patches in parallel (type: int; default: 4)
       -sac SA_CACHE_RATE, --sa_cache_rate SA_CACHE_RATE
                             percentage of raw data that is loaded into cpu during
                             segmentation (type: float; default: 0.0)
       -sab SA_BATCH_SIZE, --sa_batch_size SA_BATCH_SIZE
                             number of image patches being processed by the model
                             in parallel on gpu (type: int; default: 4)
       -samc SA_MONTE_CARLO, --sa_monte_carlo SA_MONTE_CARLO
                             use Monte Carlo dropout (default: 0)
       -sav, --sa_visualize_results
                             visualizing model output after predictions (default:
                             False)
       -sau, --sa_uncertainty_map
                             enable map (default: False)
       -sag SA_GPU_INDEX, --sa_gpu_index SA_GPU_INDEX
                             index of the GPU to use (type: int; default: 0)
       -sat SA_BINARIZATION_THRESHOLD, --sa_binarization_threshold SA_BINARIZATION_THRESHOLD
                             threshold value for binarization (type: float;
                             default: 0.5)
       -sap SA_PERCENTAGE_BRAIN_PATCH_SKIP, --sa_percentage_brain_patch_skip SA_PERCENTAGE_BRAIN_PATCH_SKIP
                             percentage threshold of patch that is brain to skip
                             during segmentation (type: float; default: 0.0)

.. table::

   =========================================  ==============================  =============================  =======================================================================================  ================================
   Flag                                       Parameter                       Type                           Description                                                                              Default
   =========================================  ==============================  =============================  =======================================================================================  ================================
   \-sai, \-\-single                          SINGLE                          ``str``                        path to raw tif/tiff data folder                                                         ``None`` (required)
   \-sao, \-\-sa_output_folder                SA_OUTPUT_FOLDER                ``str``                        path to output file folder                                                               ``None`` (required)
   \-sam, \-\-sa_model_type                   {unet,unetr,ensemble}           ``str``                        model architecture                                                                       ``None`` (required)
   \-sar, \-\-sa_resolution                   X-res Y-res Z-res               ``float`` ``float`` ``float``  voxel size                                                                               ``None`` (required)
   \-saw, \-\-sa_nr_workers                   SA_NR_WORKERS                   ``int``                        number of cpu cores deployed to pre-process image patches in parallel                    ``4``
   \-sac, \-\-sa_cache_rate                   SA_CACHE_RATE                   ``float``                      percentage of raw data that is loaded into cpu during segmentation                       ``0.0``
   \-sasw,\ \--sa_sw_batch_size               SA_SW_BATCH_SIZE                ``int``                        number of image patches being processed by the model in parallel on gpu                  ``4``
   \-samc,\ \--sa_monte_dropout               SA_MONTE_CARLO                  ``int``                        use Monte Carlo dropout                                                                  ``0``
   \-sav, \-\-sa_visualize_results            True/False                      ``bool``                       visualizing model output after predictions                                               ``False``
   \-sau, \-\-sa_uncertainty_map              True/False                      ``bool``                       enable map                                                                               ``False``
   \-sag, \-\-sa_gpu_index                    SA_GPU_INDEX                    ``int``                        index of the GPU to use                                                                  ``0``
   \-sat, \-\-sa_binarization_threshold       SA_BINARIZATION_THRESHOLD       ``float``                      threshold value for binarization                                                         ``0.5``
   \-sap, \-\-sa_percentage_brain_patch_skip  SA_PERCENTAGE_BRAIN_PATCH_SKIP  ``float``                      percentage threshold of patch that is brain to skip during segmentation                  ``0.0``
   =========================================  ==============================  =============================  =======================================================================================  ================================

.. note::

   The ``-sa`` in the flag part stands for ``segmentation ACE``.

Example usage:

.. code-block::

   $ miracl seg ace \
      -sai ./walking/subject_01/cells/ \
      -sao ./output_dir \
      -sam unet
