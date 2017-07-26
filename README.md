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

All Rights Reserved. 

____________________________


Steps to setup/run MIRACL on a Linux / Mac OS X machine:


1) Install / Check dependencies

    -> install Python 2.7 (if you do not have it)  
    
      https://www.python.org/downloads/
    
      for the required packages we recommend using Anaconda for numpy, scipy, etc:
        
      https://www.continuum.io/downloads
    
    -> install pip (if you do not have it)
    
      https://pip.pypa.io/en/stable/installing
        
    -> Run: pip install -e .   ( from inside [miracl dir] : where you placed the pipeline )
        
    -> Fiji/ImageJ
    
      https://imagej.net/Fiji/Downloads
    
    - ANTS (compiled version included in package)
    - c3d (compiled version included in package)
    
    _________________
    
    For diffusion MRI data install:

    -> MRtrix3
   
      http://www.mrtrix.org
                
    _________________

    For the visualization of nifti files and labels we recommend "ITKSNAP":
    http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3

    &

    the nifti plugin for Fiji/ImageJ
    https://imagej.nih.gov/ij/plugins/nifti.html


2) Setup user path

	-> Run user_setup.sh 
    
    This script will setup your environment (bashrc) with the following aliases:
    
    $MIRACL_HOME = localtion of pipeline and its dependencies
    
    Allen reference atlas (ara) files (with resolutions 10, 25 & 50 um):
    
    $allen10 -> Template/Atlas Image
    $lbls10  -> Annoation/Segmentation    
    $snaplut -> ITKsnap Label Descriptions
    $freelut -> Freeview Label Descriptions
    
____________________________


The pipeline is combined of different "Modules" depending on their functionality

Functions for each module are grouped together:
  
   connect -> Connectivity

   io -> Input/Output (conversion/orientation)
    
   reg -> Registration
    
   seg -> Segmentation
    
   lbls -> Labels
    
   stats -> Statistics


The workflow (flow) module combines multiple functions for ease of use to preform a desired task
     
    for example, for a standard reg/seg analysis a user would run: 
    
    1) miracl_workflow_registration_clarity-allen_wb.sh -> to perform registration of whole-brain clarity data to ARA
    
     then
    
    2) miracl_workflow_segmentation_clarity.sh -> to perform segmentation & feature extraction of full resolution clarity data 


The "Atlases" folder contains templates, annotations, histology, ontology graph info & LUT/label description of the Allen reference atlas (ARA)


The "Data" folder contains test data with example inputs and outputs for the registration and segmentation modules


for a detailed description & input parameters please check the respective wiki of each module 


You should be good to go!
