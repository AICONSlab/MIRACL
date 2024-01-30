#!/bin/bash

# get version
function getversion()
{
	ver=`cat ${MIRACL_HOME}/version.txt`
	printf "\n MIRACL pipeline v. $ver \n"
}

# help/usage function
function usage()
{
    
    cat <<usage

	1) Warps downsampled CLARITY data/channels from native space to Allen atlas

	Usage: miracl reg warp_clar

	A GUI will open to choose your:

		- < Input clarity registration folder > (clar_allen_reg)
		- < downsampled CLARITY nii to warp >
		- < ort2std.txt > 

	----------
	For command-line / scripting

	Usage: miracl reg warp_clar -r [ clar_allen registration dir ] -i [ nifti file to warp ] -o [ orient file ] -s [ seg channel ]

	Example: miracl reg warp_clar -r clar_allen_reg -i control03_05xdown_PIchan.nii.gz -o ort2std.txt

	    OR

	    miracl reg warp_clar -r clar_allen_reg -i voxelized_seg_virus.nii.gz -o ort2std.txt -s green

		arguments (required):
			r. Input clarity registration dir
			i. Input downsampled CLARITY nii to warp
			o. File with orientation to standard code

        arguments (optional):
			s. Segmentation channel (ex. green) - required if voxelized seg is input
      v. Voxel resolution (10 or 25; default: 25um)

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

c3dpath=`which c3d`
if [ -z ${c3dpath} ]; then
    printf "\n ERROR: c3d not initialized .. please setup miracl & rerun script \n"
	exit 1
else 
	printf "\n C3D path check: OK...\n" 	
fi

# ANTs
ANTS=`which antsRegistration`
if [[ -z ${ANTS} ]];
  then
    echo "ANTS program can't be found. Please (re)define \$ANTSPATH in your environment."
    exit 1
else
	printf "\n ANTS path check: OK... \n"
fi

#----------
# GUI for CLARITY input imgs
function choose_folder_gui()
{
	local openstr=$1
	local _inpath=$2

	folderpath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f folder -s "$openstr")

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
	
	eval ${_inpath}="'$folderpath'"

}

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	filepath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f file -s "$openstr")

	filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
	
	eval ${_inpath}="'$filepath'"

}

# Select Mode : GUI or script
if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":r:i:o:s:v:" opt; do

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

            s)
            	channel=${OPTARG}
            	;;

            v)
              voxres=${OPTARG}
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

    if [ -z ${inimg} ];
	then
		usage
		echo "ERROR: < -i => input CLARITY image to warp> not specified"
		exit 1
	fi

    if [ -z ${ortfile} ];
	then
		usage
		echo "ERROR: < -o=> ort file with code> not specified"
		exit 1
	fi

  if [[ $voxres -eq 10 ]]; then
    allenref=${ATLASES_HOME}/ara/template/average_template_10um.nii.gz
  elif [[ $voxres -eq 25 ]]; then
    allenref=${ATLASES_HOME}/ara/template/average_template_25um_OBmasked.nii.gz
  else
    usage
    printf "\nVoxel resolution does not match 10 or 25! Exiting!\n\n"
    exit 1
  fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_folder_gui "Clarity registration folder" regdir

	choose_file_gui "Input downsampled CLARITY to warp" inimg

	choose_file_gui "File with orientation code" ortfile

	# check required input arguments
	if [ -z ${regdir} ];
	then
		usage
		echo "ERROR: <input clarity registration dir> was not chosen"
		exit 1
	fi

fi

printf "\n ${regdir} \n"
printf "\n ${inimg} \n"
printf "\n ${ortfile} \n"
printf "\n ${channel} \n"
printf "\n ${voxres} \n"

# get time
START=$(date +%s)

# output log file of script
exec > >(tee -i ${regdir}/warp_clar_allen_script.log)
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

	if [[ ! -f ${outfile} ]]; then

		printf "\n $outstr \n"; 
		echo "$fun"; 
		eval "$fun"; 

	else  
		
		printf "\n $outstr \n"; 
		echo "$fun"; 
		eval "$fun"; 
		# printf "\n $outfile already exists ... skipping \n"; 

	fi ; 

}


#---------------------------

function warpclartoallen()
{
	

	# In imgs
	local allenref=$1
	local inimg=$2

	# In tforms
	local antswarp=$3
	local antsaff=$4
	local initform=$5

	# Out lbls
	local wrpclar=$6

	# Ort pars
	local orttagclar=$7
	local ortintclar=$8
	local orttypeclar=$9
	local ortclar=${10}

	# comb def
	local init_allen=${11}
	local comb_def=${12}

	# org clar
	local org_clar=${13}
	local res_org_clar=${14}
	local cp_clar=${15}

	# seg chan
	local res_vox=${16}
	local swp_vox=${17}
	local channel=${18}

# printf "\nCheck input:\n"
# printf "allenref: ${allenref}\n"
# printf "inimg: ${inimg}\n"
# printf "antswarp: ${antswarp}\n"
# printf "antsaff: ${antsaff}\n"
# printf "initform: ${initform}\n"
# printf "wrpclar: ${wrpclar}\n"
# printf "orttagclar: ${orttagclar}\n"
# printf "ortintclar: ${ortintclar}\n"
# printf "orttypeclar: ${orttypeclar}\n"
# printf "ortclar: ${ortclar}\n"
# printf "init_allen: ${init_allen}\n"
# printf "comb_def: ${comb_def}\n"
# printf "org_clar: ${org_clar}\n"
# printf "res_org_clar: ${res_org_clar}\n"
# printf "cp_clar: ${cp_clar}\n"
# printf "res_vox: ${res_vox}\n"
# printf "swp_vox: ${swp_vox}\n"
# printf "channel: ${channel}\n"

    # if warping seg

    # printf "\n Channel inside: ${channel} \n"
    # printf "\n res_vox inside: ${res_vox} \n"
    # printf "\n swp_vox inside: ${swp_vox} \n"

    if [[ -z "${channel}" ]]; then
        # orient to org
        ifdsntexistrun ${ortclar} "Orienting CLARITY to standard orientation" \
	    c3d ${inimg} -orient ${orttagclar} -pad 15% 15% 0 -interpolation ${ortintclar} -type ${orttypeclar} -o ${ortclar}
    else
        ifdsntexistrun ${res_vox} "Resampling CLARITY to Allen resolution" \
        ResampleImage 3 ${inimg} ${res_vox} 0.025x0.025x0.025 0

        ifdsntexistrun ${swp_vox} "Orienting CLARITY to standard orientation" \
        PermuteFlipImageOrientationAxes 3 ${res_vox} ${swp_vox}  1 2 0  0 0 0

        # orient to org
        ifdsntexistrun ${ortclar} "Orienting CLARITY to standard orientation" \
        c3d ${swp_vox} -orient ${orttagclar} -pad 15% 15% 0 -interpolation ${ortintclar} \
         -type ${orttypeclar} -o ${ortclar}
    fi



    # if [[ ! -z ${channel} ]]; then
    # if [[ ${channel} != "None" ]]; then
    #
    #     ifdsntexistrun ${res_vox} "Resampling CLARITY to Allen resolution" \
    #     ResampleImage 3 ${inimg} ${res_vox} 0.025x0.025x0.025 0
    #
    #     ifdsntexistrun ${swp_vox} "Orienting CLARITY to standard orientation" \
    #     PermuteFlipImageOrientationAxes 3 ${res_vox} ${swp_vox}  1 2 0  0 0 0
    #
    #     # orient to org
    #     ifdsntexistrun ${ortclar} "Orienting CLARITY to standard orientation" \
    #     c3d ${swp_vox} -orient ${orttagclar} -pad 15% 15% 0 -interpolation ${ortintclar} \
    #      -type ${orttypeclar} -o ${ortclar}
    #
    # else
    #     # orient to org
    #     ifdsntexistrun ${ortclar} "Orienting CLARITY to standard orientation" \
	   #  c3d ${inimg} -orient ${orttagclar} -pad 15% 15% 0 -interpolation ${ortintclar} -type ${orttypeclar} -o ${ortclar}
    #
    # fi

    org_dim=`PrintHeader ${ortclar} 2`

    ifdsntexistrun ${res_org_clar} "Resampling to original resolution" \
    ResampleImage 3 ${org_clar} ${res_org_clar} ${org_dim} 1

    #ConvertImagePixelType ${res_org_clar} ${res_org_clar} 3

    ifdsntexistrun ${cp_clar} "Copying original transform" \
    c3d ${res_org_clar} ${ortclar} -copy-transform -type ${orttypeclar} -o ${cp_clar}

    # generate comb def
    ifdsntexistrun ${comb_def} "Combining deformation fields and transformations" \
    antsApplyTransforms -d 3 -r ${init_allen} -t ${antswarp} [ ${antsaff}, 1 ] -o [ ${comb_def}, 1 ]

  	# warp to registered clarity

#  	if [[ -z ${channel} ]]; then
        ifdsntexistrun ${wrpclar} "Applying ants deformations to CLARITY data" \
        antsApplyTransforms -d 3 -r ${allenref} -i ${cp_clar} -n Bspline -t [ ${initform}, 1 ] ${comb_def} -o ${wrpclar}
#    else
#        ifdsntexistrun ${wrpclar} "Applying ants deformations to CLARITY data" \
#        antsApplyTransforms -d 3 -r ${allenref} -i ${cp_clar} -t [ ${initform}, 1 ] ${comb_def} -o ${wrpclar}
#
#        c3d ${wrpclar} -binarize -o ${wrpclar}
#    fi

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
	antswarp=${regdir}/allen_clar_ants1InverseWarp.nii.gz
	antsaff=${regdir}/allen_clar_ants0GenericAffine.mat

    init_allen=${regdir}/init_allen.nii.gz
    comb_def=${regdir}/clar_allen_comb_def.nii.gz

    # In files
    org_clar=${regdir}/clar.nii.gz



    if [[ -z "${channel}" ]]; then
        res_org_clar=${regdir}/clar_res_org.nii.gz
    else
        if [[ "${channel}" == "ace_flow" ]]; then
          res_org_clar=${regdir}/clar_res_org.nii.gz
          res_vos=${regdir}/vox_seg_*_res.nii.gz
          swp_vox=${regdir}/vox_seg_*_swp.nii.gz
        else
          res_org_clar=${regdir}/clar_res_org_seg.nii.gz
          res_vos=${regdir}/vox_seg_${channel}_res.nii.gz
          swp_vox=${regdir}/vox_seg_${channel}_swp.nii.gz
        fi
    fi

    # if [[ ! -z ${channel} ]]; then
    #     res_org_clar=${regdir}/clar_res_org_seg.nii.gz
    #     res_vos=${regdir}/vox_seg_${channel}_res.nii.gz
    #     swp_vox=${regdir}/vox_seg_${channel}_swp.nii.gz
    # else
    #     res_org_clar=${regdir}/clar_res_org.nii.gz
    # fi

    motherdir=$(dirname ${regdir})

    base=`basename ${inimg}`
	clarname=${base%%.*};

	# allenref=${ATLASES_HOME}/ara/template/average_template_25um_OBmasked.nii.gz

    # Out img
	ortclar=${regdir}/${clarname}_ort.nii.gz
	cp_clar=${regdir}/${clarname}_ort_cp_org.nii.gz

  if [[ -z "${channel}" ]]; then
      wrpclar=${regdirfinal}/${clarname}_allen_space.nii.gz
  else
      if [[ "${channel}" == "ace_flow" ]]; then
        wrpclar=${regdirfinal}/${clarname}_allen_space.nii.gz
      else
        wrpclar=${regdirfinal}/${clarname}_${channel}_channel_allen_space.nii.gz
      fi
  fi

	# if [[ ! -z ${channel} ]]; then
	#     wrpclar=${regdirfinal}/${clarname}_${channel}_channel_allen_space.nii.gz
 #    else
	#     wrpclar=${regdirfinal}/${clarname}_allen_space.nii.gz
 #    fi

#	smclarres=${regdirfinal}/clar_downsample_res??um.nii.gz

    ort=`cat ${ortfile} | grep ortcode | cut -d = -f 2`

  # printf "\nCheck args:\n"
  # printf "ort: ${ort}\n"
  # printf "allenref: ${allenref}\n"
  # printf "inimg: ${inimg}\n"
  # printf "antswarp: ${antswarp}\n"
  # printf "antsaff: ${antsaff}\n"
  # printf "initform: ${initform}\n"
  # printf "wrpclar: ${wrpclar}\n"
  # printf "orttagclar: ${orttagclar}\n"
  # printf "ortintclar: ${ortintclar}\n"
  # printf "orttypeclar: ${orttypeclar}\n"
  # printf "ortclar: ${ortclar}\n"
  # printf "init_allen: ${init_allen}\n"
  # printf "comb_def: ${comb_def}\n"
  # printf "org_clar: ${org_clar}\n"
  # printf "res_org_clar: ${res_org_clar}\n"
  # printf "cp_clar: ${cp_clar}\n"
  # printf "res_vox: ${res_vos}\n"
  # printf "swp_vox: ${swp_vox}\n"
  # printf "channel: ${channel}\n"

	printf "\n\nwarpclartoallen ${allenref} ${inimg} ${antswarp} ${antsaff} ${initform} ${wrpclar} ${ort} Cubic short ${ortclar} ${init_allen} ${comb_def} ${org_clar} ${res_org_clar} ${cp_clar} ${res_vos} ${swp_vox} ${channel}\n\n"

	warpclartoallen ${allenref} ${inimg} ${antswarp} ${antsaff} ${initform} ${wrpclar} ${ort} Cubic short \
	 ${ortclar} ${init_allen} ${comb_def} ${org_clar} ${res_org_clar} ${cp_clar} ${res_vos} ${swp_vox} ${channel}


}

#--------------------
# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

printf "\n Warping of CLARITY image to Allen space and generation of ${wrpclar} done in ${DIFF} minutes. \
Have a good day! \n"
