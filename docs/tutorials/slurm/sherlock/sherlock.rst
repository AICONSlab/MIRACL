Running MIRACL commands on Sherlock (Stanford supercomputer)
############################################################

This tutorial highlights the registration workflow but a similar approach 
applies to other commands.

Setting up MIRACL (first time)
==============================

Log in to Sherlock:

.. code-block::

   $ ssh -Y username@sherlock.stanford.edu

Start an interactive session:
 
.. code-block::

   $ sdev

Move to your scratch folder:

.. code-block::

   $ cd SCRATCH

Pull (download) Singularity container:

.. code-block::

   $ singularity pull miracl_latest.sif library://aiconslab/miracl/miracl:latest

.. attention::

   ``singularity pull`` requires :program:`Singularity` version ``3.0.0`` or 
   higher. Please refer to our Troubleshooting section ("Q: Can I build a 
   :program:`Singularity` container from the latest MIRACL image on Docker 
   Hub") if you are using an older version of :program:`Singularity`.

.. tip::

   If you have a particular :program:`Singularity` container of 
   :program:`MIRACL` that you want to use on Sherlock, just copy it to the 
   servers directly using e.g. :program:`scp` or :program:`rsync` instead of 
   pulling (downloading) the latest version of :program:`MIRACL` from the 
   :program:`Singularity` registry

Copying your data to Sherlock
=============================

Copy a folder called, e.g. :file:`input_clar` with tiff files that you want to 
register to the Allen Atlas using :program:`scp`:

.. code-block::

   $ scp -r input_clar sherlock.stanford.edu:/scratch/users/<username>/clarity_registration/.

or :program:`rsync`:

.. code-block::

   $ rsync -avPhz input_clar sherlock.stanford.edu:/scratch/users/<username>/clarity_registration/.

.. attention::
   Make sure to replace ``<username>`` with your Sherlock username

Running MIRACL in an interactive session
========================================

For quick jobs that don't require much resources you can login to Sherlock:

.. code-block::

   $ ssh -Y username@sherlock.stanford.edu

Move to your scratch folder:

.. code-block::

   $ cd SCRATCH

Start interactive session:

.. code-block::

   $ sdev

Start :program:`Singularity` with binded data:

.. code-block::

   $ singularity shell miracl_latest.sif bash

Within the shell, load the GUI:

.. code-block::

   $ miraclGUI

Or use the command-line:

.. code-block::

   $ miracl lbls stats -h

.. note::
   Please consult our Troubleshooting section if you experience problems with 
   opening :program:`MIRACL`'s GUI on Sherlock

Running SBATCH jobs
===================

If you want to run jobs with specific resources for larger, longer jobs (e.g. 
running the registration workflow) you can do the following:

First get the data orientation (please check the registration tutorial for 
setting orientation):

.. code-block::

   $ miracl conv set_orient

After setting the orientation, a file called :file:`ort2std.txt` will be 
created that might look like this:

.. code-block::

   $ cat ort2std.txt
   tifdir=/scratch/users/username/clarity_registration/input_clar
   ortcode=ARS

Use that orientation code (``ARS``) in your registration workflow.

First check the workflow arguments:

.. code-block::

   $ miracl flow reg_clar -h

Assuming you wanted to run this command with the following arguments, for 
example on your data:

.. code-block::

   $ miracl flow reg_clar -f input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

Create an sbatch script named, for example ``reg_job.sbatch`` and paste the 
following lines:

.. code-block::

   #!/bin/bash
   #SBATCH --job-name=clar_reg
   #SBATCH --ntasks=1
   #SBATCH --time=05:00:00
   #SBATCH --cpus-per-task=12
   #SBATCH --mem=32G

   module load singularity
   
   singularity exec ${SCRATCH}/miracl_latest.sif miracl flow reg_clar -f ${SCRATCH}/clarity_registration/input_clar -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

.. attention::
   Note that the ``miracl`` function call comes after invoking the 
   :program:`Singularity` call ``singularity exec ${SCRATCH}/miracl_latest.sif`` 
   and that full file paths were used for the ``.sif`` container and the 
   input data

This sample job (called: ``clar_reg``) asks for 5 hours, 12 cpus and 32G of 
memory on one node. Adjust the requested resources based on the job you are 
submitting.

Next submit the sbatch script:

.. code-block::

   $ sbatch reg_job.sbatch

To check on the status of your submitted job use:

.. code-block::

   $ squeue -u $USER

.. SeeAlso::
   
   For more resources on SLURM sbatch jobs check Stanford's tutorials on 
   `submitting <https://www.sherlock.stanford.edu/docs/getting-started/submitting/>`_ 
   and `running <https://www.sherlock.stanford.edu/docs/user-guide/running-jobs/>`_ 
   jobs on Sherlock
