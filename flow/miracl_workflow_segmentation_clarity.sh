#!/usr/bin/env bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version_num.txt`
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
        For "miracl_seg_feat_extract.py" the reg_final

    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder]

    Example: `basename $0` -f my_tifs -t nuclear -s "-p C000" -e "-l reg_final/annotation_hemi_combined_25um_clar_vox.tif"

        arguments (required):

            f. Input Clarity tif dir/folder

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

        voxelized_seg.(tif/nii)  (segmnetation results voxelized to ARA resolution)
        voxelized_seg_bin.(tif/nii) (binarized version)

        clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA lables)


        Results can be openned in Fiji for visualization


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


#----------------------

# check dependencies

if [ -z ${MIRACL_HOME} ];
then

    printf "\n ERROR: MIRACL not initialized .. please run init/setup_miracl.sh  & rerun script \n"
	exit 1

fi


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


#----------------------

# get time

START=$(date +%s)


# output log file of script

exec > >(tee -i workflow_seg_clar.log)
exec 2>&1

#---------------------------
#---------------------------


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

	if [ -z ${indir} ];
	then
		usage
		echo "ERROR: < -f => input folder with clarity tifs> not specified"
		exit 1
	fi


    #---------------------------
    # Call seg

    printf "\n Running  with the following command: \n"


    if [ -z "${segopts}" ];
	then

        echo miracl_seg_clarity_neurons_wrapper.sh -f ${indir}
        miracl_seg_clarity_neurons_wrapper.sh -f ${indir}

    else

        echo miracl_convertTIFFtoNII.py -f ${indir} "${segopts}"
        miracl_convertTIFFtoNII.py -f ${indir} ${segopts}

    fi

    #---------------------------
    # Call voxelize

    printf "\n Running voxelize segmentation with the following command: \n"

    echo miracl_seg_voxelize_parallel.py -s segmentation_${type}/seg_${type}.tif
    miracl_seg_voxelize_parallel.py -s segmentation_${type}/seg_${type}.tif

    fi

    #---------------------------
    # Call feature extraction

    printf "\n Running feature extraction with the following command: \n"

    if [ -z "${extopts}" ];
	then

        echo miracl_reg_clar-allen_whole_brain.sh -s
        miracl_reg_clar-allen_whole_brain.sh -i

    else

        echo miracl_reg_clar-allen_whole_brain.sh -i niftis/${nii} "${extopts}"
        miracl_reg_clar-allen_whole_brain.sh -i niftis/${nii} ${extopts}

    fi

    #---------------------------
    #---------------------------


else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"


    #---------------------------
    # Call set orient GUI

    printf "\n Running Set orient with the following command: \n"

    echo miracl_set_orient_gui.py
    miracl_set_orient_gui.py


    #---------------------------
    # Call conversion to nii

    printf "\n Running Tiff to Nii conversion with the following command: \n"

    indir=`cat ort2std.txt | grep tifdir | cut -d = -f 2`

    echo miracl_convertTIFFtoNII.py -f ${indir}
    miracl_convertTIFFtoNII.py -f ${indir}


    #---------------------------
    # Call registration

    printf "\n Running CLARITY registration to Allen with the following command: \n"

    # last file made in niftis folder
    nii=`ls -r niftis | tail -n 1`

    echo miracl_reg_clar-allen_whole_brain.sh -i niftis/${nii}
    miracl_reg_clar-allen_whole_brain.sh -i niftis/${nii}


fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Conversion, Registration and Allen label warping done in $DIFF minutes. Have a good day!"