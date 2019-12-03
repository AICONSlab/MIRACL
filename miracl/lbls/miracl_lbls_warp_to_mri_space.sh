#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version.txt`
	printf "\n MIRACL pipeline v. $ver \n"
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

			r. Input MRI registration dir ("mri_allen_reg")

			l. input Allen Labels to warp (in Allen space)

			o. file with orientation to standard code

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

ANTSPATH="${MIRACL_HOME}/../depends/ants"
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

	${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f folder -s "$openstr"
	
	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

	rm path.txt

}

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f file -s "$openstr"

	filepath=`cat path.txt`

	eval ${_inpath}="'$filepath'"

	rm path.txt

}

# Select Mode : GUI or script
if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":r:l:o:" opt; do
    
	    case "${opt}" in

	        r)
            	regdir=${OPTARG}
            	;;

        	l)
            	lbls=${OPTARG}
            	;;

            o)
            	ortfile=${OPTARG}
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
exec > >(tee -i ${regdir}/mr_allen_lbls_warp_script.log)
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

	local betmr=$1
	local orttag=$2
	local ortint=$3
	local orttype=$4
	local ortmr=$5

	ifdsntexistrun $ortmr "Orienting MRI to standard orientation" \
	c3d $betmr -orient $orttag -interpolation $ortint -type $orttype -o $ortmr

}

function warpallenlbls()
{
	
	# In imgs
	local smmr=$1
	local lbls=$2

	# In tforms
	local antswarp=$3
	local antsaff=$4

	# Out lbls
	local wrplbls=$5
	
	# Ort pars
	local orttaglbls=$6
	local ortintlbls=$7
	local orttypelbls=$8
	local ortlbls=${9}


	# warp to registered MRI
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${smmr} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff}  -o ${wrplbls}

	# orient to org 
	orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}

}

#---------------------------
# Build main function

function main()
{

# 1) Warp Allen labels to original MRI

    # In files
    smmr=${regdir}/mr.nii.gz

	# Tforms
	antswarp=$regdir/allen_mr_ants1Warp.nii.gz
	antsaff=$regdir/allen_mr_ants0GenericAffine.mat

	base=`basename $lbls`
	lblsname=${base%%.*};

	motherdir=`dirname ${regdir}`
	regdirfinal=${motherdir}/reg_final

	# Out lbls
	wrplbls=${regdir}/${lblsname}_ants.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz

	ort=`cat ${ortfile} | grep ortcode | cut -d = -f 2`

    # setting lbl ort
    o=${ort:0:1}
    r=${ort:1:1}
    t=${ort:2:2}

    ol=${r}

    if [ ${o} == "A" ]; then
        rl="P"
    elif [ ${o} == "P" ]; then
        rl="A"
    elif [ ${o} == "R" ]; then
        rl="L"
    elif [ ${o} == "L" ]; then
        rl="R"
    elif [ ${o} == "S" ]; then
        rl="I"
    elif [ ${o} == "I" ]; then
        rl="S"
    fi

    if [ ${t} == "A" ]; then
        tl="P"
    elif [ ${t} == "P" ]; then
        tl="A"
    elif [ ${t} == "R" ]; then
        tl="L"
    elif [ ${t} == "L" ]; then
        tl="R"
    elif [ ${t} == "S" ]; then
        tl="I"
    elif [ ${t} == "I" ]; then
        tl="S"
    fi

    ortlbl="$ol$rl$tl"

	warpallenlbls ${smmr} ${lbls} ${antswarp} ${antsaff} ${wrplbls} ${ortlbl} NearestNeighbor short ${ortlbls}

}

#--------------------
# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Allen labels warping done in $DIFF minutes. Have a good day!"


#--------------------

#TODOs

# TODOhp: fix script
# TODOlp: add scripts for warping MRI & mr in same space to Allen
