#!/usr/bin/env bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version.txt`
	printf "MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{

    cat <<usage

    Workflow (wrapper) combining multiple MIRACL functions:

    1) Segments neurons in cleared mouse brain of sparse or nuclear stains in 3D
    2) Voxelizes segmentation results into density maps with Allen atlas resolution
	3) Computes features of segmented image and summarizes them per label

    Executes:

        seg/miracl_seg_clarity_neurons_wrapper.sh
        seg/miracl_seg_voxelize_parallel.py
        seg/miracl_seg_feat_extract.py


    Usage: `basename $0`

        A GUI will open to choose folder with tif files for segmentation (folder must have one channel)

        Channel type is assumed to be sparse

        For feature extraction the "reg_final/annotation_hemi_combined_(vox)um_clar_vox.tif" file must exist where the script is started

    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder]

    Example: `basename $0` -f my_tifs -t nuclear -s "-p C001" -e "-l reg_final/annotation_hemi_combined_25um_clar_vox.tif"

        arguments (required):

            f. Input Clarity tif folder/dir [folder name without spaces]

            t. Channel type: sparse (like Thy1 YFP) or nuclear (like PI)

        optional arguments (don't forget the quotes):

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


#----------------------

# check dependencies

if [ -z ${MIRACL_HOME} ];
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
#---------------------------

function choose_folder_gui()
{
	local openstrfol=$1
	local _inpathfol=$2

    folderpath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f folder -s "$openstrfol")

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	folderpath=`cat path.txt`

	eval ${_inpathfol}="'$folderpath'"

#	rm path.txt

}

function choose_file_gui()
{
	local openstrfil=$1
	local _inpathfil=$2

    filepath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f file -s "$openstrfil")

	filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	eval ${_inpathfil}="'$filepath'"

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

    printf "\n Reading input parameters \n"

	while getopts ":f:t:s:e:" opt; do

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

        	*)
            	usage
            	;;

		esac

	done


	# check required input arguments

	if [ -z "${indir}" ];
	then
		usage
		echo "ERROR: < -f => input folder with clarity tifs> not specified"
		exit 1
	fi


    #---------------------------
    # Call seg

    printf "\n Running segmentation with the following command: \n"

    if [ -z "${type}" ];
	then
        type=sparse
    fi

    if [ -z "${segopts}" ];
	then

        echo miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}"
        miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}"

    else

        echo miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}" "${segopts}"
        miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}" ${segopts}

    fi

    #---------------------------
    # Call voxelize

    printf "\n Running voxelize segmentation with the following command: \n"

    echo miracl_seg_voxelize_parallel.py -s segmentation_${type}/seg_${type}.tif
    miracl_seg_voxelize_parallel.py -s segmentation_${type}/seg_${type}.tif


    #---------------------------
    # Call feature extraction

    printf "\n Running feature extraction with the following command: \n"

    if [ -z "${extopts}" ];
	then

        echo miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif  -l reg_final/annotation_hemi_combined_25um_clar_vox.tif
        miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif  -l reg_final/annotation_hemi_combined_??um_clar_vox.tif

    else

        echo miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif "${extopts}"
        miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif ${extopts}

    fi

    #---------------------------
    #---------------------------


else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

    # Get options

    choose_folder_gui "Open clarity dir (with .tif files) by double clicking then OK" indir

	# check required input arguments

	if [ -z "${indir}" ];
	then
		usage
		echo "ERROR: <input clarity directory> was not chosen"
		exit 1
	fi

	# options gui
	opts=$(${MIRACL_HOME}/io/miracl_io_gui_options.py -t "Seg options" -f "seg type (def = sparse)" "channel prefix (ex = C001) "  -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

	type=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen seg type: $type \n"

	prefix=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen channel prefix: $prefix \n"


    choose_file_gui "Open Allen labels (registered to clarity) used to summarize features" lbls


    if [ -z "${type}" ];
	then
        type=sparse
    fi

    printf "\n Running segmentation with the following command: \n"

    if [ -z "${prefix}" ];
	then

        echo miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}"
        miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}"

    else

        echo miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}" "${prefix}"
        miracl_seg_clarity_neurons_wrapper.sh -f "${indir}" -t "${type}" ${prefix}

    fi


    #---------------------------
    # Call conversion to nii

    printf "\n Running voxelize segmentation with the following command: \n"

    echo miracl_seg_voxelize_parallel.py -s segmentation_${type}/seg_${type}.tif
    miracl_seg_voxelize_parallel.py -s segmentation_${type}/seg_${type}.tif


    #---------------------------
    # Call registration

    printf "\n Running feature extraction with the following command: \n"


    if [ -z "${lbls}" ];
	then

        echo miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif -l reg_final/annotation_hemi_combined_??um_clar_vox.tif
        miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif -l reg_final/annotation_hemi_combined_??um_clar_vox.tif

    else

        echo miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif -l $lbls
        miracl_seg_feat_extract.py -s segmentation_${type}/voxelized_seg_${type}.tif -l $lbls

    fi

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Segmentation, voxelization and feature extraction done in $DIFF minutes. Have a good day!"