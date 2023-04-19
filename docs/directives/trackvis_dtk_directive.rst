Because of their respective licenses, we could not include :program:`TrackVis` 
or :program:`Diffusion Toolkit` in our :program:`Docker` image directly. Please 
download and install them on you host machine using their installation guide. 
After they have been successfully installed, mount a volume to your 
:program:`MIRACL` :program:`Docker` container that contains the binary folder 
for :program:`TrackVis` and :program:`Diffusion Toolkit` and add the binaries 
to your ``$PATH`` within your :program:`MIRACL` :program:`Docker` container
using the mounted volume.
