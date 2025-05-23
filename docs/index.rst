.. miracl_docs documentation master file, created by
   sphinx-quickstart on Thu Mar  9 18:38:07 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MIRACL's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   about/index
   Installation <installation/installation>
   tutorials/index
   Notebooks <notebooks/notebooks>
   troubleshooting/index
   gallery/gallery
   downloads/index

.. |license_img| image:: https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-FFA500.svg
   :width: 180px
   :height: 22px

.. |downloads_img| image:: https://img.shields.io/docker/pulls/mgoubran/miracl?label=docker%20pulls
   :width: 130px
   :height: 23px

.. |circleci_img| image:: https://img.shields.io/circleci/build/github/AICONSlab/MIRACL
   :width: 100px
   :height: 23px

.. |githubstars_img| image:: https://img.shields.io/github/stars/AICONSlab/MIRACL?style=social
   :width: 90px
   :height: 23px

|license_img| |downloads_img| |circleci_img| |githubstars_img|

.. image:: ./images/MIRACL_icon.png
    :width: 550px

.. include:: ./directives/miracl_overview_directive.rst

\*\*NEW WORKFLOW/FEATURE RELEASE\*\*
"""""""""""""""""""""""""""""""""""""""""

We have released our `AI-based Cartography of Ensembles (ACE) <https://github.com/AICONSlab/MIRACL>`_ workflow, an end-to-end, automated pipeline that integrates cutting-edge deep learning segmentation models and advanced statistical methods to enable unbiased and generalizable brain-wide mapping of 3D alterations in neuronal activity, morphology, or connectivity at the sub-regional and laminar levels beyond atlas-defined regions.

The tutorial for using ACE can be found `here <https://miracl.readthedocs.io/en/latest/tutorials/workflows/ace_flow/ace_flow.html>`_.

------

We recommend using MIRACL with the Docker or Apptainer containers we provide 
but it can also be installed locally. See our 
:doc:`installation instructions <./installation/installation>` for more information.

------

**Attention**: We changed the license for **MIRACL** from ``GPL-3.0`` to ``CC BY-NC-ND 4.0`` as of version ``2.5.0``. For more information read our `LICENSE.md <https://github.com/AICONSlab/MIRACL/blob/master/LICENSE.md>`_ or go directly to the `Creative Commons <https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en>`_ website.

------

Copyright © 2025 :email:`Maged Goubran <maged.goubran@utoronto.ca>` @ 
`AICONS Lab <https://aiconslab.github.io/>`_.

All Rights Reserved.
