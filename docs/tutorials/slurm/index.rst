HPC/SLURM clusters
##################

:program:`MIRACL` was built with HPC/SLURM clusters in mind. We recommend 
:program:`Singularity` as it is well suited to run in a cluster environment. 
We provide a :program:`Singularity` container of :program:`MIRACL's` latest 
version that can be pulled to a node directly from our online repo.

We provide tutorials on how to use :program:`MIRACL` on Compute Canada and 
Sherlock (supercomputer at Stanford university) but the principles explained 
here will be similar to other SLURM clusters.

.. note::
   If you would like to add a tutorial for a particular cluster that you are 
   working with that is missing here, we invite you to add it to this section 
   by submitting a 
   `PR <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests>`_
   (note that we write Sphinx documentation in ``.rst`` format) through our 
   `official GitHub <https://github.com/AICONSlab/MIRACL>`_.

.. toctree::
   :maxdepth: 2
   :caption: Table of contents:
   :hidden:

   Compute Canada <compute_canada/compute_canada>
   Sherlock <sherlock/sherlock>

