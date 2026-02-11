Example and atlases data
########################

Sample data you can use to test :program:`MIRACL` and the data for the atlases 
used by :program:`MIRACL` can be found here:

`Dropbox Data Link <https://www.dropbox.com/sh/i9swdedx7bsz1s8/AABpDmmN1uqPz6qpBLYLtt8va>`_

The :file:`Atlases` folder contains templates, annotations, histology, ontology 
graph info and LUT/label description of the Allen Reference Atlas (ARA).

The :file:`Data` folder contains test data with example inputs and outputs for 
the registration and segmentation modules.

For a detailed description and input parameters please check the respective 
help or :doc:`tutorial <../../../tutorials/index>` of each module.

.. note::
   The sample data used in the :doc:`ACE workflow tutorials <../../../tutorials/workflows/ace_flow/ace_flow>` is hosted on HuggingFace and can be downloaded from
   `here <https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/sample_data/ace/ace_sample_data_mode_2.zip>`__ (Mode 2) and `here <https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/sample_data/ace/ace_sample_data_stats.zip>`__ (stats). For convenience,
   the data can also be downloaded directly from within a :program:`MIRACL`
   container using:

   .. code-block::

      $ cd <WHERE YOU WANT TO DOWNLOAD DATA>
      $ download_sample_data

   This will open an interface where you can select which dataset you want to
   download.
