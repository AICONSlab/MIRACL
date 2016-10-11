#!/bin/bash
# Maged Goubran, mgoubran@stanford.edu

if [ "$#" -lt "1" ]
then
 echo "Converts dicoms in sub-directories to nii"
 echo ""
 echo "Usage: $0 <Subject directory>"
 echo ""

 exit 0
fi

motherdir=$1

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