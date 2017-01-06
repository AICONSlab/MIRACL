#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/init/version_num.txt`
	printf "MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{
    
    cat <<usage

    1) Extracts features from segmented clarity data using 3D partcile analysis
	2) summarizes the data per label (Allen atlas label)

	Runs a Fiji/ImageJ macro 
	
	Usage: `basename $0` 

	A GUI will open to choose your:

		- input clarity segmentation (seg.tif)

		- input registered allen atlas labels in clarity space (allen_labels )

		----------

	For command-line / scripting

	Usage: `basename $0` -s <clarity seg> -l <allen atlas labels> 

	Example: `basename $0` -s myclaritydata/segmentation/seg.tif -d myclaritydata/final/allen_labels  .tif

		arguments (required):

			s. Input clarity segmentation (seg.tif)

			l. Input registered allen atlas labels in clarity space (allen_labels )

		----------		

	Dependencies:
	
		- Fiji 

		- Fiji Plugins:

		Mathematical Morphology plugins 
		http://imagej.net/MorphoLibJ

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2016
	mgoubran@stanford.edu
	
	-----------------------------------

usage
getversion >&2

}

# Call help/usage function
if [[ "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then
    
    usage >&2
    exit 1

fi

#----------

# check dependencies

fijidir=`which c3d`

if [[ -z "${fijidir// }" ]]; 
then
	printf "\n ERROR: Fiji not initialized .. please install it (& the required plugins) & rerun script \n"
	exit 1
else 
	printf "\n Fiji path check: OK...\n" 	
fi

#------------


# GUI for CLARITY input imgs

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	python ${MIRACL_HOME}/io/miracl_file_folder_gui.pyc -f file -s "$openstr"
	
	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":s:l:" opt; do
    
	    case "${opt}" in

	        s)
            	seg=${OPTARG}
            	;;
	        l)
            	lbls=${OPTARG}
            	;;        	
        	*)
            	usage            	
            	;;

		esac
	
	done    	


	# check required input arguments

	if [ -z ${seg} ];
	then
		usage
		echo "ERROR: < -s => input clarity segmentation> not specified"
		exit 1
	fi

	if [ -z ${lbls} ];
	then
		usage
		echo "ERROR: < -l => input allen atlas labels> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "Please open the clarity segmentation (seg.tif)" seg

	choose_file_gui "Please open the registered allen atlas labels" lbls
	
	# check required input arguments

	if [ -z ${seg} ];
	then
		usage
		echo "ERROR: < -s => input clarity segmentation> not specified"
		exit 1
	fi

	if [ -z ${lbls} ];
	then
		usage
		echo "ERROR: < -l => input allen atlas labels> not specified"
		exit 1
	fi

fi


# get time

START=$(date +%s)

# get macro
macro=${MIRACL_HOME}/seg/miracl_analyze_particles_clarity_3D.ijm

motherdir=$(dirname ${seg})

outxls=${motherdir}/clarity_features_allen_labels.xls

if [[ ! -f $outxls ]]; then

	printf "\n Performing feature extraction using Fiji \n"
			
	echo Fiji -macro "$motherdir $seg $lbls"  | tee $log 
	Fiji -macro $macro "$motherdir $seg $lbls" | tee $log
		
else

	echo "Feature extraction already computed ... skipping"

fi

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Feature extraction done in $DIFF minutes. Have a good day!"