#!/usr/bin/env bash

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

    Workflow (wrapper) combining multiple MIRACL functions:

    1) Sets orientation of input data using a GUI
    2) Converts TIFF to NII
	3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
	4) Warps Allen annotations to the original high-res CLARITY space
	5) Warps the higher-resolution CLARITY to Allen space

    Executes:

        io/miracl_set_orient_gui.py (if run in GUI mode)
        io/miracl_convertTIFFtoNII.py
        reg/miracl_reg_clar-allen_whole_brain.sh

    Usage: `basename $0`

        A GUI will open to set data orientation
        For the "miracl_convertTIFFtoNII.py" & "miracl_reg_clar-allen_whole_brain.sh" default parameters will be chosen

    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder]  -o [out nii name]

    Example: `basename $0` -f my_tifs -o stroke2 -conv '-d 5' -reg '-m combined -v 25'

        arguments (required):

            f. Input Clarity tif dir/folder

            o. Orient code
                to orient nifti from original orientation to "standard/Allen" orientation

        optional arguments (don't forget the quotes):

            conversion to nii (invoked by -conv):

            d.  [ Downsample ratio (default: 5) ]
            cn. [ chan # for extracting single channel from multiple channel data (default: 1) ]
            cp. [ chan prefix (string before channel number in file name). ex: C00 ]
            ch. [ output chan name (default: eyfp) ]
            vx. [ original resolution in x-y plane in um (default: 5) ]
            vz. [ original thickness (z-axis resolution / spacing between slices) in um (default: 5) ]
            c.  [ nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

            Registration (invoked by -reg):

            m. Warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
            accepted inputs are: <split> or <combined>  (default: split)

			v. Labels voxel size/Resolutin of labels in um
				accepted inputs are: 10, 25 or 50  (default: 10)

			l. image of input Allen Labels to warp (default: annotation_hemi_split_10um.nii.gz - which are at a resolution of 0.01mm/10um)
				input could be at a different depth than default labels

				If l. is specified (m & v cannot be speficied)

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


#----------

# get time

START=$(date +%s)


# make reg dir

regdirfinal=$PWD/reg_final
regdir=$PWD/clar_allen_reg


if [[ ! -d $regdir ]]; then

	printf "\n Creating registration folder\n"
	mkdir -p $regdirfinal $regdir

fi

# output log file of script

exec > >(tee -i ${regdir}/workflow_reg_clar_allen.log)
exec 2>&1


#---------------------------
#---------------------------

# Select Mode : GUI or script

#if [[ "$#" -gt 1 ]]; then
#
#	printf "\n Running in script mode \n"
#
#    printf "\n Reading input parameters \n"
#
#	while getopts ":f:o:l:m:v:" opt; do
#
#	    case "${opt}" in
#
#            f)
#            	indir=${OPTARG}
#            	;;
#
#            o)
#            	ort=${OPTARG}
#            	;;
#
#            d)
#            	dr=${OPTARG}
#            	;;
#
#        	cn)
#            	cn=${OPTARG}
#            	;;
#
#            cp)
#            	cp=${OPTARG}
#            	;;
#
#            ch)
#            	ch=${OPTARG}
#            	;;
#
#        	vx)
#            	vx=${OPTARG}
#            	;;
#
#	        vz)
#            	vz=${OPTARG}
#            	;;
#
#	        c)
#            	c=${OPTARG}
#            	;;
#
#        	l)
#            	lbls=${OPTARG}
#            	;;
#
#        	m)
#            	hemi=${OPTARG}
#            	;;
#        	v)
#            	vox=${OPTARG}
#            	;;
#        	*)
#            	usage
#            	;;
#
#		esac
#
#	done


if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

    printf "\n Reading input parameters \n"

	while getopts ":f:o:l:m:v:" opt; do

	    case "${opt}" in

            f)
            	indir=${OPTARG}
            	;;

            o)
            	ort=${OPTARG}
            	;;

            conv)
            	conv=${OPTARG}
            	;;

        	reg)
            	reg=${OPTARG}
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


	if [ -z ${ort} ];
	then
		usage
		echo "ERROR: < -o => input orient code for data> not specified"
		exit 1
	fi

    #---------------------------
    # Call conversion to nii

    printf "\n Running Tiff to Nii conversion with the following command: \n"

    if [ -z ${conv} ];
	then

        miracl_convertTIFFtoNII.py -f ${indir}

    fi

    #---------------------------
    # Call registration



#---------------------------
#---------------------------


else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "Down-sampled auto-fluorescence (or Thy1) channel (nii/nii.gz)" inclar

	# check required input arguments

	if [ -z ${inclar} ];
	then
		usage
		echo "ERROR: <input clarity nii> was not chosen"
		exit 1
	fi

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Conversion, Registration and Allen label warping done in $DIFF minutes. Have a good day!"