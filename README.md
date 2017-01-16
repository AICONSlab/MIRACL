MIRACL README
______________

MIRACL (Multi-modal Image Registration and Atlasing via Clarity-based Light-microscopy)
is a general-purpose pipeline for automated:

	1) Registration of mice clarity data to Allen atlas
		a. Full brain
		b. Sections

	2) Segmentation of mice clarity data in 3D
	    a. Sparse staining
	    b. Nuclear staining

	3) Registration of mice MRI/CT data to Allen atlas
		a. Full brain
		b. Sections

	4) Connectivity analysis
	    a. Region of Interests
	    b. Specific Labels

	5) Atlas generation & Labels
	    a.


(c) Maged Goubran, 
    mgoubran@stanford.edu

@ Stanford University, 2016

____________________________


Steps to setup/run MIRACL on Linux machine:


1) Setup path

	-> Run <miracl dir>/init/setup_miracl.sh 

	<miracl dir> is where you placed the pipeline


2) Install / Check dependencies

	
	How to install python / required libraries
	
	sudo apt-get install python-tk
	
	install pip

	How to install Fiji / required plugins


	For detailed instructions on how to install of dependencies please check dependencies.txt

    For the visualization of nifti files and labels we recommand "ITKSNAP":
    http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3


You should be good to go!
