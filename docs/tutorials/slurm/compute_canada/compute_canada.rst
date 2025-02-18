Running MIRACL on Compute Canada
################################

This tutorial highlights the registration workflow but a similar approach
applies to other commands.

When using Compute Canada, :program:`MIRACL` can be used as a 
:program:`Apptainer` container.

Copy your data to Compute Canada
================================

For example, to copy a folder called :file:`input_clar` containing tiff files 
you want to register to the Allen Atlas use:

.. code-block::

   $ scp -r input_clar niagara.computecanada.edu:/scratch/<username>/.

or 

.. code-block::

   $ rsync -avPhz input_clar <username>@niagara.computecanada.edu:/scratch/<username>/.

Alternatively, for large datasets, or if you desire a GUI, you can setup a Globus transfer server by following instructions on the `Digital Research Alliance of Canada wiki <https://docs.alliancecan.ca/wiki/Transferring_data>`_.  

Log in to Compute Canada server
===============================

Log in to the Compute Canada server you copied your data to:

.. code-block::
   
   $ ssh -XY <username>@niagara.computecanada.edu

Setting up and using MIRACL
===========================

Load the specific Apptainer module you would like to use (e.g. Apptainer 1.3.5):

.. code-block::

   $ module load apptainer/1.3.5

.. note::
   Not specifying the version will load the latest version available on your node

Since :program:`MIRACL` will take up a significant amount of space, it is 
recommended to download and work with the :program:`MIRACL` 
:program:`Apptainer` container in the scratch directory. First, navigate 
there:

.. code-block::
   
   $ cd $SCRATCH

Then either build or directly download a :program:`MIRACL` :program:`Apptainer`
container. For example, building the container would be done with:

.. code-block::

   $ apptainer build miracl_latest.sif docker://mgoubran/miracl:latest

To download a :program:`MIRACL` Apptainer binary directly, do either of the 
following:

.. code-block::

   $ wget https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/apptainer/versions/miracl_v242.sif

or

.. code-block::

   $ curl -L -O https://huggingface.co/datasets/AICONSlab/MIRACL/resolve/dev/apptainer/versions/miracl_v242.sif

.. note::

   Replace the version number with the version of MIRACL you want to download.

.. note::

   If you have a particular :program:`Apptainer` container of :program:`MIRACL`
   that you want to use on Compute Canada, just copy it to the servers directly 
   using e.g. ``scp`` or ``rsync`` instead of building or downloading the latest 
   version of :program:`MIRACL` from the :program:`Apptainer` registry

Start the :program:`MIRACL` :program:`Apptainer` container with the default 
folders mounted:

.. code-block::

   $ apptainer shell miracl_latest.sif bash

:program:`Apptainer` will automatically mount your scratch folder to your 
container. If you need to mount a specific directory into a specific location, 
use the following:

.. code-block::

   $ apptainer shell -v <location_outside_container>/<source_mount>:<location_in_container>/<target_mount> miracl_latest.sif bash

Once you are logged in to the container, load the GUI from the shell:

.. code-block::

   $ miraclGUI

.. note::
   Please consult our :doc:`Troubleshooting <../../../troubleshooting/troubleshooting_singularity>` 
   section on :program:`Apptainer` if you experience problems with opening 
   :program:`MIRACL's` GUI on Compute Canada

Or use :program:`MIRACL` from the command line. For example, run 
:program:`MIRACL's` CLARITY registration workflow on the folder that you copied 
over previously:

.. code-block::

   $ miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

.. note::
   If you have a particular :program:`Apptainer` container of :program:`MIRACL` that you 
   want to use on Compute Canada, just copy it to the servers directly using 
   e.g. ``scp`` or ``rsync`` instead of pulling (downloading) the latest 
   version of :program:`MIRACL` from the :program:`Apptainer` registry

.. |linktoworkshop| replace:: :doc:`here <../../../downloads/workshops/2024/stanford_20_03_2024/stanford_20_03_2024>`

.. include:: ../../../directives/tutorial_notebook_links.txt

