Local installation
##################

.. include:: ../directives/troubleshooting_icon_directive.rst

|question| I get the following error whenever I try to run the GUI: qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "{anaconda path}/envs/miracl_merge/lib/python3.7/site-packages/cv2/qt/plugins" even though it was found
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

If you know the path to the environment name, try running the following line to 
remove the specific file in question:

.. code-block::

   rm "{path_to_environment_name}/lib/python3.7/site-packages/cv2/qt/plugins/platforms/libqxcb.so"
