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

    Workflow (wrapper) for structure tensor analysis (STA):

    1) Converts Tiff stack to nii (& down-sample)
    2) Uses registered labels to create seed mask & creates brain mask
	3) Run STA analysis
    4) Computes viral signal per registered labels

    Executes:

        io/miracl_io_convertTifftoNII.py
        utils/miracl_extract_lbl.py
        utils/miracl_create_brainmask.py
        sta/miracl_sta_track_primary_eigen.py
        lbls/miracl_lbls_stats.py


    Usage: `basename $0`

        A GUI will open to choose folder with tif files for STA and the registered Allen labels

        and choosing STA parameters
  
    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder] -r [Reg final dir]

    Example: `basename $0` -f my_tifs -r clar_reg_final -o output_sta_dir -c output_labels_info.csv -n "-d 5 -ch autofluo"

        arguments (required):

            f. Input Clarity tif folder/dir [folder name without spaces]

            r. CLARITY final registration folder

            o. output sta dir

            n.

        optional arguments (do not forget the quotes):

            conversion (invoked by -n " "):                            

                    d.  [ Downsample ratio (default: 5) ]
                    cn. [ chan # for extracting single channel from multiple channel data (default: 1) ]
                    cp. [ chan prefix (string before channel number in file name). ex: C00 ]
                    ch. [ output chan name (default: eyfp) ]
                    vx. [ original resolution in x-y plane in um (default: 5) ]
                    vz. [ original thickness (z-axis resolution / spacing between slices) in um (default: 5) ]
                    c.  [ nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

			    
	----------

	Main Outputs



    ----------

    Dependencies:

        - Matlab

        - Python 2.7

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

exec > >(tee -i workflow_sta.log)
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

	while getopts ":f:r:n:" opt; do

	    case "${opt}" in

            f)
            	indir="${OPTARG}"
            	;;

            r)
                regdir="${OPTARG}"
                ;;

            n)
            	convopts="${OPTARG}"
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
    # Call conversion to nii

    printf "\n Running conversion to nii with the following command: \n"

    printf "\n miracl_io_convertTifftoNII.py -f ${indir} ${convopts} \n"
    miracl_io_convertTifftoNII.py -f ${indir} ${convopts}

    #---------------------------
    # Call extract lbl

    printf "\n Running label extraction with the following command: \n"

    reglbls=${regdir}/

    printf "\n miracl_extract_lbl.py -i ${reglbls} -l seed_mask.nii.gz \n"
    miracl_extract_lbl.py -i ${reglbls} -l seed_mask.nii.gz

    #---------------------------
    # Call create brain mask

    printf "\n Running brain mask creation with the following command: \n"

    miracl_create_brainmask.py

    #---------------------------
    # Call STA

    printf "\n Running voxelize segmentation with the following command: \n"

    miracl_sta_track_primary_eigen.sh

    #---------------------------
    # Call lbl stats

    printf "\n Running signal statistics with the following command: \n"

    miracl_lbls_stats.py 

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

#    if [ -z "${prefix}" ];
#	then
#
#
#
#    else
#
#
#    fi


    #---------------------------
    # Call STA

    printf "\n Running voxelize segmentation with the following command: \n"



    #---------------------------
    # Call lbls stats

    printf "\n Running feature extraction with the following command: \n"

#
#    if [ -z "${lbls}" ];
#	then
#
#
#    else
#
#
#    fi

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "STA and signal analysis done in $DIFF minutes. Have a good day!"