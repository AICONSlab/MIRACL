Label statistics
################

Given an input volume and a label mask, generate a table of statistics for each label 
in the label mask.

CLI
===

To get more information about the workflow and its required arguments 
use the following command on the CLI:

.. code-block::

   $ miracl stats lbls_stats -h

Main Inputs
-----------

Input volume and registered Allen labels.

Arguments
---------

:program:`lbls_stats` requires at least two input arguments:

.. table::

   ================  =======  =====================================================  ========
   Flags             Type     Description                                            Default
   ================  =======  =====================================================  ========
   \-i, \-\-invol    ``str``  Input volume                                           Required
   \-l, \-\-lbls     ``str``  Registered Allen lbls                                  Required
   ================  =======  =====================================================  ========

The rest of the arguments are optional:
   
.. table::

   ================  =======  =====================================================  ================================
   Flags             Type     Description                                            Default
   ================  =======  =====================================================  ================================
   \-o, \-\-outfile  ``str``  Output file name                                       ``clarity_label_statistics.csv``
   \-s, \-\-sort     ``str``  Sort values by, options are:                           ``Mean``
                           
                              * ``Mean``
                              * ``StdD``
                              * ``Max``
                              * ``Min``
                              * ``Count``
                              * ``Vol(mm^3)``

                              Mean -> mean intensity values

                              Count -> number of voxels
   \-m, \-\-hemi     ``str``  Labels hemi, options are:                              ``Combined``
        
                              * ``Combined``
                              * ``Split``

   \-d, \-\-depth    ``int``  Labels depth                                           ``None`` i.e. not used
   \-r, \-\-ratio    ``str``  Tractography (.trk) file used to generate tract ratio  ``None`` i.e. not used
   ================  =======  =====================================================  ================================

Main Outpus
-----------

csv file containing the label statistics per brain region (default: ``clarity_label_statistics.csv``).

