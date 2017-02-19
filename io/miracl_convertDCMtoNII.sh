#!/bin/bash


# get version
function getversion()
{
	ver=`cat ${MIRACL_HOME}/init/version_num.txt`
	printf "MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{

    cat <<usage

    Converts dicoms in sub-directories to nii & renames sub-directories with sequence name

    Usage: `basename $0` -p < parent dir >

        arguments (required):

        -p parent directory containing sub-directories with different sequences (with dcm files)

    ----------

	Dependencies:

	    - dcm2nii
	    - c3d

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

c3dpath=`which c3d`

if [ -z ${c3dpath} ];
then
	printf "\n ERROR: c3d not initialized .. please setup miracl & rerun script \n"
	exit 1
else
	printf "\n c3d path check: OK... \n"
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

pushd ${motherdir}

for subdir in `ls -1d *`
do 

n=`ls ${subdir}/*.dcm 2>/dev/null | wc -l`
n2=`ls ${subdir}/dcm/*.dcm 2>/dev/null | wc -l`
nnii=`ls ${subdir}/*.nii* 2>/dev/null | wc -l`

	if [[ "$nnii" -gt 0 ]]; then
		
		echo "nifti files already exit in $subdir .. skipping"

	else		

		if [[ "$n" -gt 2 ]]; then

			echo "converting files in $subdir"

#			dcmdir-info-mgh ${subdir} > $subdir/dirinfo.txt
			pushd ${subdir}

			# freesurfer
#			series=`mri_probedicom --i $dcm1 | grep SeriesDescription`;
#			name=${series##*Description}
#			seq=`echo $name | tr " " "_"`
#			sernum=`mri_probedicom --i ${dcm1} | grep SeriesNo | cut -d ' ' -f2`;

            dcm1=`ls -1d *.dcm | head -1`
			seq=`c3d ${dcm1} -info-full | grep 103e | cut -d '=' -f 2`

			sernum=`c3d ${dcm1} -info-full | grep "0020|0011" | cut -d '=' -f 2`

			echo ${seq}
#			mri_convert -i ${dcm1} -o ${seq}.nii.gz
			dcm2nii -g N -x N -r N -d N -p N -e N -f Y *
            filename="${dcm1%.*}.nii"
            mv ${filename} ${seq}.nii
            gzip ${seq}.nii
			mkdir -p dcm
			mv *.dcm dcm/.
			popd

			mv ${subdir} ${seq}_${sernum}

		elif [[ "$n2" -gt 2 ]]; then
			
			echo "converting files in $subdir/dcm "

#			dcmdir-info-mgh ${subdir} > $subdir/dirinfo.txt
			pushd ${subdir}

            # freesurfer
#			series=`mri_probedicom --i $dcm2 | grep SeriesDescription`;
#			name=${series##*Description}
#			seq=`echo $name | tr " " "_"`
#           sernum=`mri_probedicom --i $dcm2 | grep SeriesNo | cut -d ' ' -f2`;

            dcm2=`ls -1d dcm/*.dcm | head -1`
			seq=`c3d ${dcm2} -info-full | grep 103e | cut -d '=' -f 2`

            sernum=`c3d ${dcm2} -info-full | grep "0020|0011" | cut -d '=' -f 2`

			echo ${seq}
#			mri_convert -i ${dcm2} -o ${seq}.nii.gz
            dcm2nii -g N -x N -r N -d N -p N -e N -f Y *
            filename2="${dcm2%.*}.nii"
            mv ${filename2} ${seq}.nii
            gzip ${seq}.nii

			popd

			mv ${subdir} ${seq}_${sernum}

		else

			echo "no dicoms (or only one) in $subdir .. skipping"

		fi

	fi

done

popd

echo ""
echo "Conversion done. Have a good day!"