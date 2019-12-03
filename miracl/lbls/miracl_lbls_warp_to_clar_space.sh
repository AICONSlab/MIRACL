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

	1) Warps Allen annotations to the original high-res CLARITY space

	Usage: `basename $0`

	A GUI will open to choose your:

		- < Input clarity registration folder >

		- < Labels to warp>

    Looks for ort2std.txt in directory where script is run

	----------

	For command-line / scripting

	Usage: `basename $0` -r [ clarity registration dir ] -l [ labels in allen space to warp ] -o [ orient file ]

	Example: `basename $0` -r clar_reg_allen -l annotation_hemi_combined_25um_grand_parent_level_3.nii.gz -o ort2std.txt

		arguments (required):

			r. Input clarity registration dir

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
ANTS=${ANTSPATH}/antsRegistration

if [[ ! -s ${ANTS} ]];
then
    printf "\n ERROR: ANTS not initialized .. please install it & rerun script \n"
	exit 1
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


# GUI for CLARITY input imgs
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
		echo "ERROR: < -r => input clarity registration dir> not specified"
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

	choose_folder_gui "Clarity registration folder" regdir

	choose_file_gui "Input labels to warp" lbls

	# check required input arguments
	if [ -z ${regdir} ];
	then
		usage
		echo "ERROR: <input clarity registration dir> was not chosen"
		exit 1
	fi

fi

# get time
START=$(date +%s)

# output log file of script
exec > >(tee -i ${regdir}/clar_allen_lbls_warp_script.log)
exec 2>&1

#---------------------------
#---------------------------

# 1) Process clarity Functions
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

	ifdsntexistrun $ortclar "Orienting CLARITY to standard orientation" \
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

    # Vox
    local vox=${16}

    # Res clar
    local smclarres=${17}

    # Upsample ref
    vres=`python -c "print(${vox}/1000.0)"`

    # res clar in
    ifdsntexistrun ${smclarres} "Usampling reference image" ResampleImage 3 ${smclar} ${smclarres} ${vres}x${vres}x${vres} 0 1

	# warp to registered clarity
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${smclarres} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff} ${initform} -o ${wrplbls}

	# orient to org
	ifdsntexistrun ${ortlbls} "Orienting Allen labels" orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}

	# swap dim (x=>y / y=>x)
	ifdsntexistrun ${swplbls} "Swapping label dimensions" PermuteFlipImageOrientationAxes  3 ${ortlbls} ${swplbls}  1 0 2  0 0 0

	# create tif lbls
	ifdsntexistrun ${tiflbls} "Converting lbls to tif" c3d ${swplbls} -type ${orttypelbls} -o ${tiflbls}

	# upsample to img dimensions
    df=`echo ${inclar} | egrep -o "[0-9]{2}x_down" | egrep -o "[0-9]{2}"`

     # get img dim
    alldim=`PrintHeader ${inclar} 2`
    x=${alldim%%x*} ;
    yz=${alldim#*x} ; y=${yz%x*} ;
    z=${alldim##*x} ;

    ox=$(($y*$df)) ;
    oy=$(($x*$df)) ;

    # create hres tif lbls
	ifdsntexistrun ${restif} "Converting high res lbls to tif" c3d ${swplbls} -resample ${ox}x${oy}x${z}mm -interpolation ${ortintlbls} -type ${orttypelbls} -o ${restif}

}

#---------------------------
# Build main function

function main()
{

# 1) Warp Allen labels to original CLARITY

    regdirfinal=$PWD/reg_final

    if [[ ! -d ${regdirfinal} ]]; then

        printf "\n Creating registration folder\n"
        mkdir -p ${regdirfinal}

    fi

	# Tforms
	initform=${regdir}/init_tform.mat
	antswarp=${regdir}/allen_clar_ants1Warp.nii.gz
	antsaff=${regdir}/allen_clar_ants0GenericAffine.mat

	base=`basename $lbls`
	lblsname=${base%%.*};

    # In files
    smclar=${regdir}/clar.nii.gz

    motherdir=$(dirname ${regdir})

    # last file made in niftis folder
    inclar=`ls -r ${motherdir}/niftis | tail -n 1`

    # Out lbls
	wrplbls=${regdirfinal}/${lblsname}_clar_downsample.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
	swplbls=${regdir}/${lblsname}_ants_swp.nii.gz
	tiflbls=${regdirfinal}/${lblsname}_clar_vox.tif
	reslbls=${regdirfinal}/${lblsname}_clar.nii.gz
	restif=${regdirfinal}/${lblsname}_clar.tif

    lblsdim=`PrintHeader ${lbls} 1`
    xlbl=${lblsdim%%x*}

    vox=`python -c "print (${xlbl}*1000.0)"`

	smclarres=${regdirfinal}/clar_downsample_res${vox}um.nii.gz

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


	warpallenlbls ${smclar} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} ${ortlbl} NearestNeighbor short ${ortlbls} ${swplbls} ${tiflbls} ${inclar} ${reslbls} ${restif} ${vox} ${smclarres}


}

#--------------------
# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Allen labels warping done in $DIFF minutes. Have a good day!"
