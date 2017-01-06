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

	1) Warps Allen annotations to the MRI space

	Usage: `basename $0`

	A GUI will open to choose your:

		- < Input MRI registration folder >

		- < Labels to warp>

	----------

	For command-line / scripting

	Usage: `basename $0` -i <input_down-sampled_MRI_nifti>

	Example: `basename $0` -i Reference_channel_05_down.nii.gz

		arguments (required):

			r. Input MRI registration dir

			l. input Allen Labels to warp (in Allen space)

		optional arguments:
		

	----------		

	Dependencies:
	
		- ANTs
		https://github.com/stnava/ANTs			
		
		- c3d
		https://sourceforge.net/projects/c3d

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2016
	mgoubran@stanford.edu
	
	-----------------------------------

	registration based on ANTs	

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


if [ -z ${ANTSPATH} ];
then
	printf "\n ERROR: ANTS not initialized .. please install it & rerun script \n"
	exit 1
else 
	printf "\n ANTS path check: OK... \n" 
fi

c3ddir=`which c3d`

if [[ -z "${c3ddir// }" ]]; 
then
	printf "\n ERROR: C3D not initialized .. please install it & rerun script \n"
	exit 1
else 
	printf "\n C3D path check: OK...\n" 	
fi

#----------
# Init atlas dir
atlasdir=${MIRACL_HOME}/atlases

# GUI for MRI input imgs
function choose_folder_gui()
{
	local openstr=$1
	local _inpath=$2

	${MIRACL_HOME}/io/miracl_file_folder_gui.py -f folder -s "$openstr"
	
	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

	rm path.txt

}

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	${MIRACL_HOME}/io/miracl_file_folder_gui.py -f file -s "$openstr"

	filepath=`cat path.txt`

	eval ${_inpath}="'$filepath'"

	rm path.txt

}

# Select Mode : GUI or script
if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":r:l:" opt; do
    
	    case "${opt}" in

	        r)
            	regdir=${OPTARG}
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
	if [ -z ${regdir} ];
	then
		usage
		echo "ERROR: < -r => input MRI registration dir> not specified"
		exit 1
	fi

    if [ -z ${lbls} ];
	then
		usage
		echo "ERROR: < -l => labels> not specified"
		exit 1
	fi

else

	# call gui
	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_folder_gui "MRI registration folder" regdir

	choose_file_gui "Input labels to warp" lbls

	# check required input arguments
	if [ -z ${regdir} ];
	then
		usage
		echo "ERROR: <input MRI registration dir> was not chosen"
		exit 1
	fi

fi

# get time
START=$(date +%s)

# output log file of script
exec > >(tee -i ${regdir}/clar_allen_script.log)
exec 2>&1

#---------------------------
#---------------------------

# 1) Process MRI Functions
# Function to check if file exists then runs other command

function ifdsntexistrun() 
{  

	local outfile="$1"; 
	local outstr="$2"; 
	local fun="${@:3}";  

	if [[ ! -f $outfile ]]; then 

		printf "\n $outstr \n"; 
		echo "$fun"; 
		eval "$fun"; 

	else  
		
		printf "\n $outfile already exists ... skipping \n"; 

	fi ; 

}

#---------------------------

# Orient
function orientimg()
{

	local betclar=$1
	local orttag=$2
	local ortint=$3
	local orttype=$4
	local ortclar=$5

	ifdsntexistrun $ortclar "Orienting MRI to standard orientation" \
	c3d $betclar -orient $orttag -interpolation $ortint -type $orttype -o $ortclar

}

function warpallenlbls()
{
	
	# In imgs
	local smclar=$1
	local lbls=$2

	# In tforms
	local antswarp=$3
	local antsaff=$4
	local initform=$5

	# Out lbls
	local wrplbls=$6
	
	# Ort pars
	local orttaglbls=$7
	local ortintlbls=$8
	local orttypelbls=$9
	local ortlbls=${10}

	# swap lbls
	local swplbls=${11}
	local tiflbls=${12}
	
	# Up lbls
    local inclar=${13}
    local reslbls=${14}
    local restif=${15}

	# warp to registered MRI
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${smclar} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff} ${initform} -o ${wrplbls}

	# orient to org 
#	orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}

}

#---------------------------
# Build main function

function main()
{

# 1) Warp Allen labels to original MRI

	# Tforms
	antswarp=$regdir/allen_clar_ants1Warp.nii.gz
	antsaff=$regdir/allen_clar_ants0GenericAffine.mat

	base=`basename $lbls`
	lblsname=${base%%.*};

	# Out lbls
	wrplbls=${regdir}/${lblsname}_ants.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
	swplbls=${regdir}/${lblsname}_ants_swp.nii.gz
	tiflbls=${regdir}/${lblsname}_ants.tif
	reslbls=${regdirfinal}/allen_lbls_clar_ants.nii.gz
	restif=${regdirfinal}/allen_lbls_clar_ants.tif

	warpallenlbls ${smclar} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} RPI NearestNeighbor short ${ortlbls} ${swplbls} ${tiflbls} ${inclar} ${reslbls} ${restif}
}

#--------------------
# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Registration and Allen label warping done in $DIFF minutes. Have a good day!"