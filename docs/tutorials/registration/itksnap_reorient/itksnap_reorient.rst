itk-SNAP re-orient image
========================

Chosing the correct image orientation is crucial for the registration to work.
:program:`itk-SNAP` let's you change your image orientation manually using their 
``Reorient Image`` tool. This tutorial will teach you how to use 
:program:`itk-SNAP` to manually re-orient an image from ``LPI`` to ``ARI``.

1. Load your image into :program:`itk-SNAP` like you would normally do.

.. image:: ./images/1_main_screen.png

2. Under ``Tools`` select ``Reorient Image...``

.. image:: ./images/2_reorient_menu_open.png

3. In the menu that will open, you will be presented with the current 
   orientation of your image on the left, and the new orientation on the right.

.. image:: ./images/3_reorient_menu_main.png

4. To change the orientation either enter the ``RAI`` orientation code directly
   in the ``RAI Code:`` text field, or change the ``x``, ``y`` and ``z`` axes
   of the image until the desired orientation is achieved. The preview window
   on the bottom right will give you an indication of where you are in 3D space.

.. image:: ./images/4_reorient_menu_reoriented.png

5. Once the correct orientation has been confirmed and the changes are applied,
   the ``Reorient Image`` menu can be closed. Your image will now appear in the
   new orientation :program:`itk-SNAP`'s main window.

.. image:: ./images/5_main_screen_reoriented.png

6. Save the newly oriented image manually or click ``Save`` when exiting
   :program:`itk-SNAP`. Click on ``Close without Saving`` if you don't want to 
   save the image in its new orientation.

.. image:: ./images/6_save_changes_menu.png
