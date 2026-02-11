Apptainer
#########

.. include:: ../directives/troubleshooting_icon_directive.rst

|question| Can I build a Apptainer container from the latest MIRACL image on Docker Hub
---------------------------------------------------------------------------------------

Absolutely! To do so, however, you will need to grab a development node after 
logging in to the cluster. If you try pulling from the login node, you will 
use a ton of memory building the SIF image, and the process will be killed (in 
other words, it won't work).

.. code-block::

   $ sdev

or

.. code-block::

   $ salloc

Once you have your node, you can then build the container:

.. code-block::

   $ cd $SCRATCH
   $ apptainer build miracl_latest.sif docker://mgoubran/miracl:latest

|question| Processes that require TrackVis or Diffusion Toolkit are not working
-------------------------------------------------------------------------------

.. include:: ../directives/trackvis_dtk_directive.rst

|question| I get the following error whenever I try to run the GUI from within the Apptainer container on Compute Canada
------------------------------------------------------------------------------------------------------------------------

.. code-block::

   qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
   This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

   Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.
   
We do not recommend trying to make X11 forwarding work directly from the 
terminal. You should use VNC instead. Follow the instructions 
`here <https://docs.alliancecan.ca/wiki/VNC>`_. Once you are connected to your 
login or compute node with VNC, you will see a desktop environment. Open a 
terminal there and follow :doc:`our tutorials <../tutorials/slurm/index>` on how 
to use :program:`MIRACL` with :program:`Apptainer` on clusters.

If you for some reason need to run the :program:`MIRACL` GUI directly in the 
terminal, using a :program:`Apptainer` container and X11, try the following 
workarounds:

Login Nodes
^^^^^^^^^^^

Exit your :program:`Apptainer` container and start a VNC server (for 3600sec 
or more as required) on your login node:

.. code-block::

   vncserver -MaxConnectionTime 3600

The first time the VNC server is started you will prompted for a password (do 
not leave this blank). Once done, check if a X11 socket is available for your 
username:

.. code-block::

   ls -la /tmp/.X11-unix/

.. note::
   If no socket is available for your username, log out and log back in to your 
   login node

Start another :program:`Apptainer` container and try to run ``miraclGUI`` 
again from within it.

Compute Nodes
^^^^^^^^^^^^^

Exit your :program:`Apptainer` container and set an environment variable on 
your allocated compute node:

.. code-block::

   export XDG_RUNTIME_DIR=${SLURM_TMPDIR}

Start a VNC server:

.. code-block::

   vncserver

Start another :program:`Apptainer` container and try to run ``miraclGUI`` 
again from within it.
