#!/usr/bin/env bash

# get version
function getversion()
{
	ver=`cat ${MIRACL_HOME}/version.txt`
	printf "MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{

    cat <<usage

    Workflow (wrapper) combining multiple MIRACL functions:

    1) Segments neurons in cleared mouse brain of virus, cFOS, sparse or nuclear stains in 3D
    2) Voxelizes segmentation results into density maps with Allen atlas resolution
	3) Computes features of segmented image and summarizes them per registered labels

    Executes:

        seg/miracl_seg_clarity_neurons_wrapper.sh
        seg/miracl_seg_voxelize_parallel.py
        seg/miracl_seg_feat_extract.py


    Usage: `basename $0`

        A GUI will open to choose folder with tif files for segmentation (folder must have one channel)

        For feature extraction the "reg_final/annotation_hemi_combined_(vox)um_clar_vox.tif" file must exist

    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder]

    Example: `basename $0` -f my_tifs -t nuclear -s "-p C001" -e "-l reg_final/annotation_hemi_combined_25um_clar_vox.tif"

        arguments (required):

            f. Input Clarity tif folder/dir [folder name without spaces]

            t. Channel type: virus or cFOS or sparse (like Thy1 YFP) or nuclear (like PI)

            v. Registered labels voxel size (10, 25, or 50um)

        optional arguments (do not forget the quotes):

            Segmentation (invoked by -s " "):

			    p. Channel prefix & number if multiple channels (like Filter0001)

            Feature extraction (invoked by -e " "):

                l. Allen labels (registered to clarity) used to summarize features

                    reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif


	----------

	Main Outputs


        segmentation/seg.tif (.mhd) or seg_nuclear.tif (.mhd) : segmentation image with all labels (cells)
        segmentation/seg_bin.tif (.mhd) or seg_bin_nuclear.tif (.mhd) : binarized segmentation image

        voxelized_seg.(tif/nii)  (segmentation results voxelized to ARA resolution)
        voxelized_seg_bin.(tif/nii) (binarized version)

        clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA labels)


        Results can be opened in Fiji for visualization


    ----------

    Dependencies:

		- Fiji

		- Fiji Plugins:

		1) 3D Segmentation plugins (3D ImageJ suite)
		http://imagejdocu.tudor.lu/doku.php?id=plugin:stacks:3d_ij_suite:start

		2) Mathematical Morphology plugins
		http://imagej.net/MorphoLibJ

	-----------------------------------

	(c) Maged Goubran @ Stanford University, 2017
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


#----------------------

# check dependencies

if [[ -z ${MIRACL_HOME} ]];
then

    printf "\n ERROR: MIRACL not initialized .. please run init/setup_miracl.sh  & rerun script \n"
	exit 1

fi


#----------------------

# get time

START=$(date +%s)


# output log file of script

exec > >(tee -i workflow_seg_clar.log)
exec 2>&1

#---------------------------


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

    printf "\n Reading input parameters \n"

	while getopts ":f:t:s:e:v:" opt; do

	    case "${opt}" in

            f)
            	indir="${OPTARG}"
            	;;

            t)
            	type="${OPTARG}"
            	;;

            s)
            	segopts="${OPTARG}"
            	;;

        	e)
            	extopts="${OPTARG}"
            	;;

        	v)
            	vox="${OPTARG}"
            	;;

        	*)
            	usage
            	;;

		esac

	done


	# check required input arguments

	if [[ -z "${indir}" ]];
	then
		usage
		echo "ERROR: < -f => input folder with clarity tifs> not specified"
		exit 1
	fi


    #---------------------------
    # Call seg

    printf "\n Running segmentation with the following command: \n"

    if [[ -z "${type}" ]];
	then
        type=virus
    fi

    if [[ -z "${segopts}" ]];
	then

        echo miracl seg clar -f "${indir}" -t "${type}"
        miracl seg clar -f "${indir}" -t "${type}"

    else

        echo miracl seg clar -f "${indir}" -t "${type}" "${segopts}"
        miracl seg clar -f "${indir}" -t "${type}" ${segopts}

    fi

    #---------------------------
    # Call voxelize

    printf "\n Running voxelize segmentation with the following command: \n"

    echo miracl seg voxelize -s segmentation_${type}/seg_${type}.tif -v ${vox}
    miracl seg voxelize -s segmentation_${type}/seg_${type}.tif -v ${vox}


    #---------------------------
    # Call feature extraction

    printf "\n Running feature extraction with the following command: \n"

    if [[ -z "${extopts}" ]];
	then

        echo miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif  -l reg_final/annotation_hemi_combined_??um_clar_vox.tif
        miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif  -l reg_final/annotation_hemi_combined_??um_clar_vox.tif

    else

        echo miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif "${extopts}"
        miracl seg feat_extract  -s segmentation_${type}/voxelized_seg_${type}.tif ${extopts}

    fi

    #---------------------------
    #---------------------------


else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	# options gui
	opts=$(${MIRACL_HOME}/conv/miracl_conv_gui_options.py -t "Seg options" \
	     -d "Input tiff dir" \
	     -v "Registered allen labels (..clar_vox.tif) in the reg_final dir" \
	     -f "seg type [virus (def), cFOS, sparse or nuclear]" "channel prefix (ex = C001) " "labels voxel size" -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

	# check required input arguments
	lbls="$(echo -e "${arr[0]}" | cut -d ':' -f 2 | tr -d '[:space:]')"

    printf "\n Chosen registered labels: ${lbls} \n"

    indir="$(echo -e "${arr[1]}" | cut -d ':' -f 2 | tr -d '[:space:]')"

	if [[ -z "${indir}" ]];
	then
		usage
		echo "ERROR: <input clarity directory> was not chosen"
		exit 1
	fi

    printf "\n Chosen in dir: ${indir} \n"

	type="$(echo -e "${arr[2]}" | cut -d ':' -f 2 | tr -d '[:space:]')"

	printf "\n Chosen seg type: ${type} \n"

	prefix="$(echo -e "${arr[3]}" | cut -d ':' -f 2 | tr -d '[:space:]')"

    printf "\n Chosen channel prefix: ${prefix} \n"

	vox="$(echo -e "${arr[4]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
	# vox=`echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen voxel size: ${vox} \n"


    if [[ -z "${type}" ]];
	then
        type=virus
    fi

    printf "\n Running segmentation with the following command: \n"

    if [[ -z "${prefix}" ]];
	then

        echo miracl seg clar -f "${indir}" -t "${type}"
        miracl seg clar -f "${indir}" -t "${type}"

    else

        echo miracl seg clar -f "${indir}" -t "${type}" -p "${prefix}"
        miracl seg clar -f "${indir}" -t "${type}" -p ${prefix}

    fi


    #---------------------------
    # Call conversion to nii

    printf "\n Running voxelize segmentation with the following command: \n"

    echo miracl seg voxelize -s segmentation_${type}/seg_${type}.tif -v ${vox}
    miracl seg voxelize -s segmentation_${type}/seg_${type}.tif -v ${vox}

    #---------------------------
    # Call feat extract

    printf "\n Running feature extraction with the following command: \n"


    if [[ -z "${lbls}" ]];
	then

        echo miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif -l reg_final/annotation_hemi_combined_??um_clar_vox.tif
        miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif -l reg_final/annotation_hemi_combined_??um_clar_vox.tif

    else

        echo miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif -l ${lbls}
        miracl seg feat_extract -s segmentation_${type}/voxelized_seg_${type}.tif -l ${lbls}

    fi

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

miracl utils endstate -f "Segmentation, voxelization and feature extraction" -t "$DIFF minutes"
