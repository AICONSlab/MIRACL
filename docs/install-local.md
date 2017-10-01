# Local Install
Steps to setup/run MIRACL on a Linux / Mac OS X machine:

## Install / Check dependencies

### Python
[Install Python 2.7](https://www.python.org/downloads/) (if you do not have it)  
For the required packages we recommend using [Anaconda](https://www.continuum.io/downloads) for numpy, scipy, etc.
You should also install pip.
  
### Run

Then run        
    -> Run: 

      ( from inside [miracl dir] : where you placed the pipeline )

        mv io tmp

        pip install -e .

        mv tmp io

    -> install PyQt4 using anaconda, run:
        
        conda install pyqt=4
            
    -> Fiji/ImageJ
    
      https://imagej.net/Fiji/Downloads

    -> FSL

      https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation

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
    
    This script will setup your environment to add MIRACL functions to your path
    (to call them from anywhere) & with the following aliases:
    
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
