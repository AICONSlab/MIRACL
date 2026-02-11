Instance Segmentation Function
##############################

This module needs to be used in conjunction with the :doc:`ACE segmentation module <../ace_seg/ace_seg>`.

This module perfoms the following:

1. Load in the patches from ACE segmentation output folder
2. Perform connected component analysis on the patches to label neurons
3. Get region properties for each neuron
4. Save the results to a json file
5. Optionally stack the patches to form 2D image slices

.. note::

    Stacking is needed to correct the neuron count since counting 
    is done in parallel. The patches must be processed in sequence 
    to get the correct neuron count, which is done by patch stacking.


Main outputs
------------

1. Connected component patches of the neurons located at
   ``<input_folder>/cc_patches/``
2. A json file containing the region properties of each neuron 
   located at ``<input_folder>/cc_patches/neuron_info_final.json``
3. Optionally, 2D image slices of the neuron labels located at
   ``<output_folder>``


CLI
===

To look at the arguments that need to be provided to the function, invoke the 
help menu using:


.. code-block::

   $ miracl seg instance -h

The following menu will be printed to the terminal:

.. code-block::

    usage: miracl seg instance -i <input_seg_folder> [ -o <output_folder> ] [ -g <glob_pattern> ] [ -p <percentage_brain_patch_skip> ]

    Instance segmentation step of ACE segmentation
    
    This module perfoms the following:
        1. Load in the patches from ACE segmentation output folder
        2. Perform connected component analysis on the patches to label neurons
        3. Get region properties for each neuron
        4. Save the results to a json file
        5. Optionally stack the patches to form image slices
        
    Notes: stacking is needed to correct the neuron count since counting is done
    in parallel. The patches must be processed in sequence to get the correct
    neuron count, which is done by patch stacking.

    Required arguments:
    -i INPUT_FOLDER, --input_folder INPUT_FOLDER
                            Path to ACE segmentation output folder
                            (generated_patches/)
    -r RAW_INPUT_FOLDER, --raw_input_folder RAW_INPUT_FOLDER
                            Path to raw clarity tiff folder

    Optional arguments:
    -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                            Path to output folder (default: <input_folder>.parent
                            /cc_slices/)
    --properties PROPERTIES [PROPERTIES ...]
                            Properties to compute for each neurone (default:
                            ['area', 'centroid', 'bbox', 'label'])
    -g GLOB_PATTERN, --glob_pattern GLOB_PATTERN
                            Glob pattern to match files in <input_folder>
                            (default: [A-Zo]*patch_*.tiff)
    -p PERCENTAGE_BRAIN_PATCH_SKIP, --percentage_brain_patch_skip PERCENTAGE_BRAIN_PATCH_SKIP
                            Percentage of brain patch skip (default: 0.0)
    --no-stack            Stack the patches to form image slices. Default is to
                            stack the patches.
    -c CPU_LOAD, --cpu-load CPU_LOAD
                            Percentage of CPU load to use (default: 0.95)
    -h, --help            Show this help message and exit


.. table::

   ========================================  ===============================  =============================  =======================================================================================  ===========================================
   Flag                                      Parameter                        Type                           Description                                                                              Default                                    
   ========================================  ===============================  =============================  =======================================================================================  ===========================================
   \-i, \-\-input_folder                     INPUT_FOLDER                     ``str``                        Path to ACE segmentation output folder (generated_patches/)                              ``None`` (required)
   \-r, \-\-raw_input_folder                 RAW_INPUT_FOLDER                 ``str``                        Path to raw clarity tiff folder                                                          ``None`` (required)
   \-o, \-\-output_folder                    OUTPUT_FOLDER                    ``str``                        Path to output folder (default: <input_folder>.parent /cc_slices/)                       ``<input_folder>.parent /cc_slices/``
   \-\-properties                            PROPERTIES                       ``str+``                       Properties to compute for each neuron                                                    ``["area", "centroid", "bbox", "label"]``  
   \-g, \-\-glob_pattern                     GLOB_PATTERN                     ``str``                        Glob pattern to match files in <input_folder>                                            ``"[A-Zo]*patch_*.tiff"``
   \-p, \-\-percentage_brain_patch_skip      PERCENTAGE_BRAIN_PATCH_SKIP      ``float`` (0.0 to 1.0)         Percentage of brain patch skip                                                           ``0.0``
   \-\-no-stack                              N/A                              ``bool``                       Stack the patches to form image slices. Default is to stack the patches.                 ``False``
   \-c, \-\-cpu-load                         CPU_LOAD                         ``float``                      Percentage of CPU load to use                                                            ``0.95``
   ========================================  ===============================  =============================  =======================================================================================  ===========================================



Example usage:

.. code-block::

   $ miracl seg instance \
        -i generated_patches/ \
        -r raw_data/ \
        -o output_dir \
        -p 0.2