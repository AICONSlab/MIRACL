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
   troubleshooting/index
   gallery/gallery
   Data <data/example_and_atlases_data>

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

\*\*NEW FEATURE RELEASE IN EARLY 2024\*\*
"""""""""""""""""""""""""""""""""""""""""

**AI-based Cartography of Ensembles (ACE) segmentation method and workflow** 
is an end-to-end, automated pipeline that seamlessly integrates cutting-edge 
deep learning segmentation models (both Vision transformer and CNN-based 
architectures), registration algorithms, and advanced statistical methods to 
enable an unbiased and generalizable mapping of 3D alterations in neuronal 
activity, morphology, or connectivity at the sub-regional and laminar levels 
beyond atlas-defined regions.

:program:`ACE` has been develop by `Ahmadreza Attarpour <https://github.com/AAttarpour>`_,
`Maged Goubran <https://github.com/mgoubran>`_ and `Jonas Osmann <https://github.com/jono3030>`_
and will be available as part of MIRACL in **early January 2024**.

------

We recommend using MIRACL with the Docker or Singularity containers we provide 
but it can also be installed locally. See our 
:doc:`installation instructions <./installation/installation>` for more information.

Copyright © 2023 :email:`Maged Goubran <maged.goubran@utoronto.ca>` @ 
`AICONS Lab <https://aiconslab.github.io/>`_.

All Rights Reserved.
