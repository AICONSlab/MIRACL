Instance Segmentation Function
##############################

This module requires a neuron info dict from 
:doc:`the instance segmentation step <../instance_seg/instance_seg>`
as well as the Allen labels directory (in native space), typically 
from :doc:`the registration step <../../registration/clarity_allen/clarity_allen>`.

This module perfoms the following:

1. Filters cells based on a specified minimum (and optional maximum)
   area argument
2. Computes cell count of segmented image and summarizes them per label
3. Outputs clarity_segmentation_features_ara_labels.csv (segmentation
   features summarized per ARA labels)


Main outputs
------------

1. A csv file containing the segmentation features summarized per ARA labels
   located at ``<output_folder>/clarity_segmentation_features_ara_labels_<hemi>.csv``


CLI
===

To look at the arguments that need to be provided to the function, invoke the 
help menu using:


.. code-block::

   $ miracl seg count_neurons -h

The following menu will be printed to the terminal:

.. code-block::

    usage: miracl count_neurons -l LBL --min-area MIN_AREA --neuron-info-dict
                            NEURON_INFO_DICT [-o OUTPUT] [--max-area MAX_AREA]
                            [--hemi {split,combined}] [--skip SKIP]
                            [-c CPU_LOAD] [-v] [-h]

    1) Filters cells based on a specified minimum (and maximum) area argument 1)
    Computes cell count of segmented image and summarizes them per label 2)
    Outputs clarity_segmentation_features_ara_labels.csv (segmentation features
    summarized per ARA labels)

    optional arguments:
    -o OUTPUT, --output OUTPUT
                            Output directory (default: .)
    --max-area MAX_AREA   Maximum area of a neuron to be considered (default:
                            1000000)
    --hemi {split,combined}
                            Hemisphere of the brain (split or combined) (default:
                            combined)
    --skip SKIP           Number of slices to skip from start and end (default:
                            50) Note: this helps to skip the slices that are poor
                            quality due to the microscope
    -c CPU_LOAD, --cpu-load CPU_LOAD
                            Percentage of CPU load to use (default: 0.3)
    -v, --verbose         Prints out more information (default: False)
    -h, --help            show this help message and exit

    required arguments:
    -l LBL, --lbl LBL     Allen labels directory (in native space) used to
                            summarize features; from registration step. Can also
                            be any other labels that you want to use to summarize
                            the features, such as cluster labels.
    --min-area MIN_AREA   Minimum area of a neuron to be considered
    --neuron-info-dict NEURON_INFO_DICT
                            Path to the neuron info dict from instance
                            segmentation (neuron_info_final.json)


.. table::

   ========================  ======================  ============================  ==============================================================================================  ================================
   Flag                      Parameter               Type                          Description                                                                                     Default
   ========================  ======================  ============================  ==============================================================================================  ================================
   \-l, \-\-lbl              LBL                     ``str``                       Allen labels directory (in native space) used to summarize features; from registration step.    ``None`` (required)
   \-\-min-area              MIN_AREA                ``int``                       Minimum area of a neuron to be considered                                                       ``None`` (required)
   \-\-neuron-info-dict      NEURON_INFO_DICT        ``str``                       Path to the neuron info dict from instance segmentation (neuron_info_final.json)                ``None`` (required)
   \-o, \-\-output           OUTPUT                  ``str``                       Output directory                                                                                ``./``
   \-\-max-area              MAX_AREA                ``int``                       Maximum area of a neuron to be considered                                                       ``1000000``
   \-\-hemi                  {split, combined}       ``str``                       Hemisphere of the brain (split or combined)                                                     ``combined``
   \-\-skip                  SKIP                    ``int``                       Number of slices to skip from start and end                                                     ``50``
   \-c, \-\-cpu-load         CPU_LOAD                ``float``                     Percentage of CPU load to use                                                                   ``0.3``
   \-v, \-\-verbose          N/A                     ``bool``                      Prints out more information                                                                     ``False``
   ========================  ======================  ============================  ==============================================================================================  ================================

.. note::
    
    The ``--skip`` argument is used to skip the slices that are poor quality due to the microscope.


Example usage:

.. code-block::

   $ miracl seg count_neurons \
       -l ../reag_final/allen_labels/ \
       --min-area 10 \
       --neuron-info-dict ./cc_patches/neuron_info_final.json \
       -o ./output_dir