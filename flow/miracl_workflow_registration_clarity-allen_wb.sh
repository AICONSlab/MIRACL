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

    1) Sets orientation of input data using a GUI (if orient code not given)
    2) Converts TIFF to NII
	3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
	4) Warps Allen annotations to the original high-res CLARITY space
	5) Warps the higher-resolution CLARITY to Allen space

    Executes:

        io/miracl_set_orient_gui.py (if orient code not given)
        io/miracl_convertTIFFtoNII.py
        reg/miracl_reg_clar-allen_whole_brain.sh



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

