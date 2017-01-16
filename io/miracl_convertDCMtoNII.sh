#!/bin/bash
# Maged Goubran, mgoubran@stanford.edu

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

    Converts dicoms in sub-directories to nii

    Usage: `basename $0` -p < parent dir >

        arguments (required):

        -p parent directory containing sub-directories with different sequences (with dcm files)

    ----------

	Dependencies:

	    - mri_convert & mri_probedicom (from FREESURFER)

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


#----------

# check dependencies

convdir=`which mri_convert`

if [ -z ${convdir} ];
then
	printf "\n ERROR: mri_convert not initialized .. please install it from FREESURFER & rerun script \n"
	exit 1
else
	printf "\n mri_convert path check: OK... \n"
fi

probedir=`which mri_probedicom`

if [ -z ${probedir} ];
then
	printf "\n ERROR: mri_probedicom not initialized .. please install it from FREESURFER & rerun script \n"
	exit 1
else
	printf "\n mri_probedicom path check: OK... \n"
fi

#-------

while getopts ":p:" opt; do

    case "${opt}" in

        p)
            motherdir=${OPTARG}
            ;;

        *)
            usage
            ;;

    esac

done

if [ -z ${motherdir} ];
then
    usage
    echo "ERROR: < -p => input parent directory > not specified"
    exit 1
fi

#------

pushd $motherdir

for subdir in `ls -1d *`
do 

n=`ls $subdir/*.dcm 2>/dev/null | wc -l`
n2=`ls $subdir/dcm/*.dcm 2>/dev/null | wc -l`
nnii=`ls $subdir/*.nii* 2>/dev/null | wc -l`

	if [[ "$nnii" -gt 0 ]]; then
		
		echo "nifti files already exit in $subdir .. skipping"

	else		

		if [[ "$n" -gt 2 ]]; then

			echo "converting files in $subdir"

			dcmdir-info-mgh $subdir > $subdir/dirinfo.txt
			pushd $subdir
			
			dcm1=`ls -1d *.dcm | head -1`
			series=`mri_probedicom --i $dcm1 | grep SeriesDescription`;
			name=${series##*Description}
			seq=`echo $name | tr " " "_"`
			
			sernum=`mri_probedicom --i $dcm1 | grep SeriesNo | cut -d ' ' -f2`;

			echo $seq
			mri_convert -i $dcm1 -o ${seq}.nii.gz
			mkdir -p dcm
			mv *.dcm dcm/.
			popd

			mv $subdir ${seq}_${sernum}

		elif [[ "$n2" -gt 2 ]]; then
			
			echo "converting files in $subdir/dcm "

			dcmdir-info-mgh $subdir > $subdir/dirinfo.txt
			pushd $subdir

			dcm2=`ls -1d dcm/*.dcm | head -1`
			series=`mri_probedicom --i $dcm2 | grep SeriesDescription`;
			name=${series##*Description}
			seq=`echo $name | tr " " "_"`
			
			sernum=`mri_probedicom --i $dcm2 | grep SeriesNo | cut -d ' ' -f2`;

			echo $seq
			mri_convert -i ${dcm2} -o ${seq}.nii.gz

			popd

			mv $subdir ${seq}_${sernum}

		else

			echo "no dicoms (or only one) in $subdir .. skipping"

		fi

	fi

done

popd

echo ""
echo "Conversion done. Have a good day!"