MIRACL README
______________

MIRACL (Multi-modal Image Registration and Atlasing via Clarity-based Light-microscopy)
is a general-purpose, open-source pipeline for automated:

	1) Registration of mice clarity data to the Allen reference atlas

	2) Segmentation & feature extraction of mice clarity data in 3D (Sparse & nuclear staining)

	3) Registration of mice multimodal imaging data (MRI & CT, in-vivo & ex-vivo) to Allen reference atlas

	4) Label or region specific connectivity analysis based on the Allen connectivity atlas

    5) Comparison of diffusion tensort imaging (DTI)/tractography, virus tracing using CLARITY &
      Allen connectivity atlas

    6) Statistical analysis of CLARITY & Imaging data

	7) Atlas generation & Label manipulation


(c) Maged Goubran, 
    mgoubran@stanford.edu

@ Stanford University, 2016

____________________________


Steps to setup/run MIRACL on a Linux machine:


1) Setup path

	-> Run <miracl dir>/init/setup_miracl.sh 

	<miracl dir> is where you placed the pipeline


2) Install / Check dependencies

    - ANTS (compiled version included in package)
    - c3d (compiled version included in package)
    - Fiji
    - Python

	For detailed instructions on how to install different dependencies please check wiki/dependencies.txt

    For the visualization of nifti files and labels we recommand "ITKSNAP":
    http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3


You should be good to go!
