#!/bin/bash

# get version
function getversion()
{
	ver=`cat ${MIRACL_HOME}/version_num.txt`
	printf "\n MIRACL pipeline v. $ver \n"
}

# help/usage function
function usage()
{
    
    cat <<usage

	1) Warps MRI data from native space to Allen atlas

	Usage: `basename $0`

	A GUI will open to choose your:

		- < Input MRI registration folder >

		- < MRI nii to warp >

    	- < ort2std.txt > 

	----------

	For command-line / scripting

	Usage: `basename $0` -r [ MRI registration dir ] -i control03_05xdown_PIchan.nii.gz -o [ orient file ]

	Example: `basename $0` -r mr_reg_allen -i inv_T2map.nii.gz -o ort2std.txt

		arguments (required):

			r. Input MRI registration dir

			i. input MRI nii to warp 

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

	folderpath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f folder -s "$openstr")
	
	# filepath=`cat path.txt`	
	# eval ${_inpath}="'$filepath'"
	# rm path.txt

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
	
	eval ${_inpath}="'$folderpath'"

}

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	filepath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f file -s "$openstr")

	# filepath=`cat path.txt`
	# eval ${_inpath}="'$filepath'"
	# rm path.txt

	filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
	
	eval ${_inpath}="'$filepath'"

}

# Select Mode : GUI or script
if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":r:i:o:" opt; do
    
	    case "${opt}" in

	        r)
            	regdir=${OPTARG}
            	;;

        	i)
            	inimg=${OPTARG}
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

    if [ -z ${inimg} ];
	then
		usage
		echo "ERROR: < -i => input MRI image to warp> not specified"
		exit 1
	fi

    if [ -z ${ortfile} ];
	then
		usage
		echo "ERROR: < -o=> ort file with code> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_folder_gui "MRI registration folder" regdir

	choose_file_gui "Input MRI to warp" inimg

	choose_file_gui "File with orientation code" ortfile

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
exec > >(tee -i ${regdir}/warp_mr_allen_script.log)
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

	if [[ ! -f ${outfile} ]]; then

		printf "\n $outstr \n"; 
		echo "$fun"; 
		eval "${fun}";

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

	ifdsntexistrun ${ortmr} "Orienting MRI to standard orientation" \
	c3d ${betmr} -orient ${orttag} -interpolation ${ortint} -type ${orttype} -o ${ortmr}

}

function warpallenlbls()
{
	

	# In imgs
	local allenref=$1
	local inimg=$2

	# In tforms
	local antswarp=$3
	local antsaff=$4
	# local initform=$5

	# Out lbls
	local wrpmr=$5

	# Ort pars
	local orttagmr=$6
	local ortintmr=$7
	local orttypemr=$8
	local ortmr=${9}

    # orient to org
	ifdsntexistrun ${ortmr} "Orienting Allen labels" orientimg ${wrpmr} ${orttagmr} ${ortintmr} ${orttypemr} ${ortmr}

  	# warp to registered MRI
	ifdsntexistrun ${wrpmr} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${allenref} -i ${ortmr} -n Multilabel -t ${antswarp} [ ${antsaff}, 1 ] -o ${wrpmr}

}

#---------------------------
# Build main function

function main()
{

# 1) Warp Allen labels to original MRI

    regdirfinal=$PWD/reg_final

    if [[ ! -d ${regdirfinal} ]]; then

        printf "\n Creating registration folder\n"
        mkdir -p ${regdirfinal}

    fi

	# Tforms
	# initform=${regdir}/init_tform.mat
	antswarp=${regdir}/allen_mr_ants1InverseWarp.nii.gz
	antsaff=${regdir}/allen_mr_ants0GenericAffine.mat

    # In files
    smmr=${regdir}/mr.nii.gz

    motherdir=$(dirname ${regdir})

    base=`basename ${inimg}`
	mrname=${base%%.*};

	allenref=${atlasdir}/ara/template/average_template_25um.nii.gz

    # Out img
	ortlmr=${regdir}/${mrname}_ort.nii.gz
	wrpmr=${regdirfinal}/${mrname}_allen_ants.ii.gz	

#	smmrres=${regdirfinal}/mr_downsample_res${vox}um.nii.gz

    ort=`cat ${ortfile} | grep ortcode | cut -d = -f 2`

	warpallenlbls ${allenref} ${inimg} ${antswarp} ${antsaff} ${wrpmr} ${ort} NearestNeighbor short ${ortmr} 


}

#--------------------
# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Warping of MRI image to Allen space done in $DIFF minutes. Have a good day!"