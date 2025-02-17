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

.. |license_img| image:: https://img.shields.io/github/license/mgoubran/MIRACL
   :width: 117px
   :height: 23px

.. |downloads_img| image:: https://img.shields.io/docker/pulls/mgoubran/miracl?label=Docker%2FRelease%20Downloads
   :width: 230px
   :height: 23px

|license_img| |downloads_img|

.. image:: ./images/MIRACL_icon.png
    :width: 550px

.. include:: ./directives/miracl_overview_directive.rst

\*\*NEW WORKFLOW/FEATURE RELEASE\*\*
"""""""""""""""""""""""""""""""""""""""""

We have released our `AI-based Cartography of Ensembles (ACE) <https://github.com/AICONSlab/MIRACL>`_ workflow, an end-to-end, automated pipeline that integrates cutting-edge deep learning segmentation models and advanced statistical methods to enable unbiased and generalizable brain-wide mapping of 3D alterations in neuronal activity, morphology, or connectivity at the sub-regional and laminar levels beyond atlas-defined regions.

The tutorial for using ACE can be found `here <https://miracl.readthedocs.io/en/latest/tutorials/workflows/ace_flow/ace_flow.html>`_.

------

We recommend using MIRACL with the Docker or Singularity containers we provide 
but it can also be installed locally. See our 
:doc:`installation instructions <./installation/installation>` for more information.

Copyright © 2025 :email:`Maged Goubran <maged.goubran@utoronto.ca>` @ 
`AICONS Lab <https://aiconslab.github.io/>`_.

All Rights Reserved.
