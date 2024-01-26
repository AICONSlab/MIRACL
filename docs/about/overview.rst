MIRACL in a nutshell
####################

.. include:: ../directives/miracl_overview_directive.rst

Program structure
=================

:program:`MIRACL` is structured into `Modules`_ and `Workflows`_.

Modules
-------

The pipeline is comprised of different ``Modules`` depending on their 
respective functionality. Functions for each module are grouped together:

============================================  =========================
Module                                        Functionality
============================================  =========================
connect                                       Connectivity
:doc:`conv <../tutorials/conversion/index>`   Conversion (Input/Output)
:doc:`reg <../tutorials/registration/index>`  Registration
seg                                           Segmentation
lbls                                          Labels
:doc:`utilfn <../tutorials/utilities/index>`  Utilities
sta                                           Structure Tensor Analysis
stats                                         Statistics
============================================  =========================

An example of using a module would be to run the ``clar_allen`` function which 
performs a CLARITY whole-brain registration to Allen Atlas on a ``nifti`` 
image (down-sampled by a factor of five):

.. code-block::

   $ miracl reg clar_allen -i niftis/SHIELD_05x_down_autoflor_chan.nii.gz -o ARI -m combined -b 1

The above command uses the ``-i`` flag to select the nifti file, ``-o`` to 
specify the orientation of the image, ``-m`` to register to both hemispheres 
and ``-b`` to include the olfactory bulb.

Workflows
---------

The workflow (:doc:`flow <../tutorials/workflows/index>`) module combines 
multiple functions from the above modules for ease of use to perform a desired 
task.

For example, a standard reg/seg analysis could look like this:

First perform registration of whole-brain CLARITY data to ARA:

.. code-block::

   $ miracl flow reg_clar -h

Then perform segmentation and feature extraction of full resolution CLARITY data:

.. code-block::

   $ miracl flow seg -h

Or structure tensor analysis:

.. code-block::

   $ miracl flow sta -h
