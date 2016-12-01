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

	1) Segments neurons in clear mouse brain of sparse stains in 3D

	Runs a Fiji/ImageJ macro 
	
	Usage: `basename $0` 

	A GUI will open to choose your input clarity folder (with .tif files)

	The folder should contain data from one channel 

		----------

	For command-line / scripting

	Usage: `basename $0` -d <clarity dir> -t <channel type: sparse or nuclear>

	Example: `basename $0` -d my_clarity_tifs -t sparse

		arguments (required):

			d. Input clarity directory (including .tif images of one channel)

		Optional arguments:

			t. Channel type: sparse )like Thy1 YFP) [default] or nuclear (like PI)

		----------		

	Dependencies:
	
		- Fiji 

		- Fiji Plugins:
		
		1) 3D Segmentation plugins (3D ImageJ suite) 	
		http://imagejdocu.tudor.lu/doku.php?id=plugin:stacks:3d_ij_suite:start	

		2) Mathematical Morphology plugins 
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

	${MIRACL_HOME}/io/python_file_folder_gui.py -f folder -s "$openstr"
	
	folderpath=`cat path.txt`
	
	eval ${_inpath}="'$folderpath'"

	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":d:t:" opt; do
    
	    case "${opt}" in

	        d)
            	tifdir=${OPTARG}
            	;;

            t)
            	type=${OPTARG}
            	;;
        	
        	*)
            	usage            	
            	;;

		esac
	
	done    	


	# check required input arguments

	if [ -z ${tifdir} ];
	then
		usage
		echo "ERROR: < -d => input clarity directory> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "Open clarity dir (with .tif files) by double clicking then OK" tifdir
	
	# check required input arguments

	if [ -z ${tifdir} ];
	then
		usage
		echo "ERROR: <input clarity directory> was not chosen"
		exit 1
	fi

fi

# Default type to sparse
if [ -z ${type} ];
then
    type=sparse
fi

# get time

START=$(date +%s)

# get macro
macro=${MIRACL_HOME}/seg/miracl_seg_neurons_clarity_3D_${type}.ijm

#motherdir=$(dirname ${tifdir})
#inputdir=$(basename ${tifdir})
segdir=${tifdir}/segmentation

# make seg dir
if [[ ! -d ${segdir} ]];then

	printf "\n Creating Segmentation folder\n"
	mkdir -p ${segdir}

fi

# # split filters -- later

# if [[ ! -d $tifdir/filter0 ]]; then
	
# 	mkdir $tifdir/filter0 $tifdir/filter1
# 	mv $tifdir/*Filter0000* $tifdir/filter0/.
# 	mv $tifdir/*Filter0001* $tifdir/filter1/.

# fi

# free up cached memory -- needs sudo permissions
# printf "\n Freeing up cached memory \n"

# echo "sync; echo 3 | sudo tee /proc/sys/vm/drop_caches"
#sync; echo 3 | sudo tee /proc/sys/vm/drop_caches 1>/dev/null

outseg=${tifdir}/seg.mhd
log=${tifdir}/Fiji_seg_log.txt
outnii=${segdir}/seg.nii.gz

if [[ ! -f ${outseg} ]]; then

	printf "\n Performing Segmentation using Fiji \n"
			
	echo Fiji -macro $macro "${tifdir}" | tee ${log}
	Fiji -macro $macro "${tifdir}/" | tee ${log}
		
else

	echo "Segmentation already computed ... skipping"

fi

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Segmentation done in $DIFF minutes. Have a good day!"