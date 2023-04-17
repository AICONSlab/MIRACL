Workflows
#########

The workflow (``flow``) module combines multiple functions from various modules 
for ease of use to perform a desired task.

For example, a standard reg/seg analysis could look like this:

First perform registration of whole-brain CLARITY data to ARA:

.. code-block::

   $ miracl flow reg_clar -h

Then perform segmentation and feature extraction of full resolution CLARITY 
data:

.. code-block::

   $ miracl flow seg -h

Or structure tensor analysis:

.. code-block::

   $ miracl flow sta -h

.. include:: ../../directives/missing_fns_tutorials_directive.rst

.. toctree::
   :maxdepth: 2
   :caption: Table of contents:

   CLARITY-Allen registration <clarity_registration/clar_reg>
   STA <sta/sta>
   CLARITY segmentation <clarity_segmentation/clar_seg>
