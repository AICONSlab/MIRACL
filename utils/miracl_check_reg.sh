#!/bin/bash

# help/usage function
function help()
{
    
    cat <<help

   	CLARITY project / Mouse / Stroke study 

	1) Checks registration results for images 
	
	Usage: `basename $0` <group (stroke or control)> <<mouse #> <img> <viewer>

	Example: `basename $0` stroke 17 FA freeview 

	Valid options: struct, T1map, T2map, FA, MD, CT, TDI, Clar, All

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2016
	mgoubran@stanford.edu
	
	-----------------------------------

help

	exit 1

}


# Call help/usage function
if [[ $# -lt 2 || "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then
    help >&2
fi

grp=$1
id=$2
imgtype=$3
viewer=$4

projectdir=/data/clarity_project/mouse/stroke_study/${grp}

regdirfinal=$projectdir/$id/reg/final

atlasdir=/data/clarity_project/atlases
allen=$atlasdir/allen/allen_atlas_template_res0.05_reg.nii.gz
lbls=$atlasdir/allen/annotations/annotations.nii.gz

case $imgtype in
	
	'struct' )	
	img=$regdirfinal/inv_mri_allen.nii.gz

		;;

	'T1map' )	
	img=$regdirfinal/inv_T1map_allen_s0.75.nii.gz

		;;

	'T2map' )	
	img=$regdirfinal/inv_T2map_allen_s0.75.nii.gz
		;;

	'FA' )	
	img=$regdirfinal/inv_FA_allen_s0.75.nii.gz

		;;

	'MD' )	
	img=$regdirfinal/inv_MD_allen_s0.75.nii.gz

		;;

	'CT' )	
	img=$regdirfinal/exv_ct_allen.nii.gz	

		;;

	'TDI' )	
	img=$regdirfinal/inv_TDI_allen.nii.gz

		;;
	
	'Clar' )	
	img=$regdirfinal/hresclar_allen_ants.nii.gz

		;;

	'\?' )
	printf "Invalid Option \ncheck your spelling if you've been drinking!"

	exit 1

		;;

esac


if [[ $imgtype == 'All' ]]; then
	
	$viewer $allen $regdirfinal/*v*.nii.gz $regdirfinal/hres*.nii.gz $lbls

else

	$viewer $allen $img $lbls

fi
