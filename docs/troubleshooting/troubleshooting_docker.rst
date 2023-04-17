Docker
######

.. include:: ../directives/troubleshooting_icon_directive.rst

|question| MIRACL's GUI (miraclGUI) is not working
--------------------------------------------------

Access control might be enabled on your host machine. Change your ``xhost`` 
access control on your host machine (not within your :program:`Docker` 
container). Exit the running :program:`Docker` container and type:

.. code-block::

   xhost +

Log back in to your container. Reset ``xhost`` after you are done with using 
the :program:`MIRACL` GUI using:

.. code-block::

   xhost -

The above will enable/disable access for all users. If this is not the desired 
behavior, access can be granted in a more 
`fine grained manner <https://www.x.org/archive/X11R6.8.1/doc/xhost.1.html>`_.

Example:

.. code-block::

   xhost +SI:localsuer:<yourusername>

.. note::
   Replace ``<yourusername>`` with the actual user name of your host system

|question| The GUI worked before but does not work anymore
----------------------------------------------------------

Navigate to the directory that contains your ``docker-compose.yml`` and 
restart the container with ``docker compose down`` followed by docker ``compose 
up -d``. The GUI should work again.

|question| I cannot run X or Y with Docker because of permission denied errors
------------------------------------------------------------------------------

If you have not set up a :program:`Docker` user you might need to run 
:program:`Docker` commands with ``sudo``. While this should work, setting up a 
:program:`Docker` user is the prefered.

|question| Processes that require TrackVis or Diffusion Toolkit are not working
-------------------------------------------------------------------------------

.. include:: ../directives/trackvis_dtk_directive.rst

|question| STA workflow fails when trying to create tracts
----------------------------------------------------------

Make sure that the :program:`TrackVis` and :program:`Diffusion Toolkit` 
binaries are available to :program:`MIRACL`. See the previous question for 
details.

|question| I need to install or make changes to apps in the MIRACL container but my user is not authorized to do so
-------------------------------------------------------------------------------------------------------------------

The user in the container is the user of your host machine. This is done to 
avoid issues with the :program:`MIRACL` GUI and X11. If you need to make 
changes that require ``sudo`` privileges, just log out of your container and 
log back in as root:

.. code-block::

   $ docker exec -it -u root miracl bash

After making your changes, log out and log back in with your regular user:

.. code-block::

   $ docker exec -it miracl bash

.. attention::
   Always remembert that changes to the container are not persistent. If you
   need to make permanent changes as ``sudo``, add them to the ``Dockerfile``
   instead.

|question| MIRACL's GUI (miraclGUI) does not work anymore after my ssh connection has been broken
-------------------------------------------------------------------------------------------------

Assuming you logged back in with ssh and are in the container, exit the 
container and restart it using ``docker compose down`` and ``docker compose up 
-d`` .

Shell back into the container and the GUI should work again.

.. include:: ../directives/docker_compose_directive.rst

|question| I do not want to create the image using the provided script
----------------------------------------------------------------------

You can build the image yourself, not using the script we provide. However, 
the build script makes sure that the GUI version of :program:`MIRACL` works 
with :program:`Docker` and it is therefore recommended to use it. Build the 
image with:

.. code-block::

   $ docker build -t mgoubran/miracl .

.. note::
   Do not forget the ``.`` at the end of the command. It is required to point 
   ``docker build`` to the ``Dockerfile``.

To run the container use:

.. code-block::

   $ docker run -it mgoubran/miracl bash

.. attention::
   If you make changes in the container that are not stored on a volume, make 
   sure to use the same container the next time you run :program:`MIRACL` as 
   changes made to a container will only apply to this specific container. If you 
   run :program:`MIRACL` again from the same image using ``docker run -it 
   mgoubran/miracl bash``, a new container will be created that does not contain 
   the changes you made to the first container.

.. warning::
   The :program:`MIRACL` GUI will be unlikely to work out-of-the-box but you 
   can try the troubleshooting steps in the following section to make it work.

|question| I get either or both of the following errors whenever I try to run the GUI from within a Docker container that was build without the provided build script
---------------------------------------------------------------------------------------------------------------------------------------------------------------------

.. code-block::

   Authorization required, but no authorization protocol specified
   qt.qpa.xcb: could not connect to display :1

.. note::
   The number for the display could be different in your case

.. code-block::

   qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
   This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

   Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.

Exit your running :program:`Docker` container and run the following to mount 
an X11 socket from the host system in a new :program:`Docker` container:

.. code-block::

   docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mgoubran/miracl bash

If you still receive the above error, you may have to change your xhost access 
control. See previous troubleshooting step above.
