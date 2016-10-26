#!/bin/bash

# help/usage function
function usage()
{
    
    cat <<usage

   	MIRACL pipeline / CLARITY project / Mouse  

	1) Registers in-vivo or ex-vivo MRI data to Allen Atlas 

	
	Usage: `basename $0` -p <project name> -g <group> -m <mouse #> -v <in or ex vivo>

	Example: `basename $0` -p stroke_study -g stroke -m 17 -v in


	arguments:
		
		p. Project name (equivalent to name in init/project_<name>.txt)

		g. Group (example: stroke or control)

		m. Mouse number 

		v. 'in'-vivo or 'ex'-vivo

		Looks for <inv_or_exv>_mri.nii.gz in <mouse #>/<inv_or_exv>_MRI/struct and stroke_mask.nii.gz (segmentation) if stroke mouse

	
	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2016
	mgoubran@stanford.edu
	
	-----------------------------------

	
	registration based on: 
	
	ANTs 
	https://github.com/stnava/ANTs/
	
	NiftyReg
	http://sourceforge.net/projects/niftyreg/

	-----------------------------------	

usage

	exit 1

}


# Call help/usage function
if [[ $# -lt 2 || "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then
    usage >&2
fi

while getopts ":p:g:m:v:" opt; do
    
    case "${opt}" in
       
        p)
            projname=${OPTARG}
            ;;
        g)
            grp=${OPTARG}
            ;;
        m)
            mid=${OPTARG}
            ;;
        v)
        	vivo=${OPTARG}    
        	;;
        *)
            usage
            ;;
	esac
done

# check required input arguments

if [ -z ${projname} ];
then
	usage
	echo "ERROR: < -p => project name> not specified"
	exit 1
fi


if [ -z ${grp} ];
then
	usage
	echo "ERROR: < -g => group> not specified"
	exit 1
fi


if [ -z ${mid} ];
then
	usage
	echo "ERROR: < -m => mouse id> not specified"
	exit 1
fi

if [ -z ${vivo} ];
then
	usage
	echo "ERROR: < -v => in or ex vivo> not specified"
	exit 1
fi

if [ -z ${MIRACL_HOME} ];
then
	usage
	echo "ERROR: < MIRACL not initialized .. please run init/setup_miracl.sh > not specified"
	exit 1
fi

#----------

# check dependencies

fslcmd=`which fsl`

if [ -z "${fslcmd// }" ];
then
	echo "ERROR: < FSL not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
fi

if [ -z ${ANTSPATH} ];
then
	echo "ERROR: < ANTS not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
fi

if [ -z ${FREESURFER_HOME} ];
then
	echo "ERROR: < FREESURFER not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
fi

c3ddir=`which c3d`

if [[ -z "${c3ddir// }" ]]; 
then
	echo "ERROR: < C3D not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
fi

niftydir=`which reg_aladin`

if [[ -z "${niftydir// }" ]]; 
then
	echo "ERROR: < C3D not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
fi


#----------

# Read init project dirs

projectdir=`cat ${MIRACL_HOME}/init/project_${projname}.txt`

atlasdir=`cat ${MIRACL_HOME}/init/atlasesdir.txt`


# Setup init files

grpdir=${projectdir}/${grp}

inmr=${grpdir}/$mid/${vivo}v_MRI/struct/${vivo}v_mri.nii.gz
stroke_mask=${prgdir}/$mid/${vivo}v_MRI/struct/stroke_mask.nii.gz 


# Allen brain atlas

orgallen=${atlasdir}/allen/allen_atlas_template.nii.gz
allenref=${atlasdir}/allen/allen_atlas_template_res0.05_reg.nii.gz


# make reg dir
regdir=${grpdir}/${mid}/reg/${vivo}v_mri_allen
regdirfinal=${grpdir}/${mid}/reg/final


if [[ ! -d $regdir ]];then

	printf "\n Creating registration folder\n"
	mkdir -p $regdir $regdirfinal

fi


# output log file of script
exec > >(tee -i ${regdir}/${vivo}v_mri_allen_script.log)
exec 2>&1


# get time
START=$(date +%s)


#---------------------------


# 1) Process MRI

# N4 bias correct
biasmr=$regdir/${vivo}v_mri_bias.nii.gz

if [[ ! -f $biasmr ]];then

	printf "\n Bias-correcting MRI with N4 \n"

	echo N4BiasFieldCorrection -d 3 -i $inmr -o $biasmr
	N4BiasFieldCorrection -d 3 -i $inmr -o $biasmr

fi


# threshold
thrmr=$regdir/${vivo}v_mri_bias_thr.nii.gz

if [[ ! -f $thrmr ]];then

	printf "\n Thresholding MRI \n"

	echo fslmaths $biasmr -thrP 40 $thrmr
	fslmaths $biasmr -thrP 40 $thrmr

fi


# Crop
dims=`fslstats $thrmr -w`

cropmr=$regdir/${vivo}v_mri_bias_thr_crop.nii.gz
cropmask=$regdir/stroke_mask_crop.nii.gz

if [[ ! -f $cropmr ]]; then

	printf "\n Cropping MRI \n"

	echo fslroi $thrmr $cropmr $dims
	fslroi $thrmr $cropmr $dims
	
	if [ "$grp" == "stroke" ]; then

		printf "\n Also cropping stroke mask \n"

		echo fslroi $stroke_mask $cropmask $dims
		fslroi $stroke_mask $cropmask $dims

	fi

fi 


# change header * 10 dims
hdmr=$regdir/${vivo}v_mri_bias_thr_crop_hd.nii.gz

if [[ ! -f $hdmr ]]; then

	printf "\n Altering MRI header \n"

	echo c3d $cropmr -spacing 1.172x1.172x5mm $hdmr
	c3d $cropmr -spacing 1.172x1.172x5mm $hdmr

fi


# get COM
com=`fslstats $hdmr -C`

# Bet
betmr=$regdir/${vivo}v_mri_hd_roi_thr_bet.nii.gz

if [[ ! -f $betmr ]]; then
	
	printf "\n Skull striping MRI \n"

	echo bet $hdmr $betmr -r 55 -c $com -f 0.3
	bet $hdmr $betmr -r 55 -c $com -f 0.3

fi


# orient MRI

ortmr=$regdir/${vivo}v_mri_hd_roi_thr_bet_ort.nii.gz
ortmask=$regdir/stroke_mask_crop_ort.nii.gz

if [[ ! -f $ortmr ]];then

	printf "\n Orienting MRI & stroke mask to standard orientation \n"

	ort=`mri_info $inmr | grep "Orientation" | cut -d ' ' -f 5`

	if [[ "$ort" == "RAI" ]]; then
		
		newort=RSA

	elif [[ "$ort" == "RPS" ]]; then
		
		newort=RPI

	fi

	echo c3d $betmr -orient $newort -interpolation Cubic -o $ortmr
	c3d $betmr -orient $newort -interpolation Cubic -o $ortmr 

	if [ "$grp" == "stroke" ]; then

		printf "\n Also orienting stroke mask \n"

		echo c3d $cropmask -orient $newort -interpolation NearestNeighbor -o $ortmask 		
		c3d $cropmask -orient $newort -interpolation NearestNeighbor -o $ortmask 

	fi	

fi

# update back hdr
reginmr=$regdir/${vivo}v_mri_reg.nii.gz

if [[ ! -f $reginmr ]]; then

	printf "\n Updating back header \n"

	echo c3d $ortmr -spacing 0.1172x0.1172x0.5mm $reginmr
	c3d $ortmr -spacing 0.1172x0.1172x0.5mm $reginmr

fi

regmask=$regdir/stroke_${vivo}v_mask.nii.gz

# invert mask and copy geometry 

if [ "$grp" == "stroke" ]; then

	printf "\n Inverting mask for registration \n"

	if [[ ! -f $regmask ]]; then
		
		echo fslmaths $ortmask -binv $regmask
		fslmaths $ortmask -binv $regmask
				
		echo fslcpgeom $reginmr $regmask
		fslcpgeom $reginmr $regmask

	fi

fi


#---------------------------


# 2) Register MRI to Allen with ANTS

# Ants registration parameters

# transform
trans=a #Affine
# cross correlation radius
rad=8
# get num of threads 
thrds=`nproc`

antsmr=$regdir/${vivo}v_mri_allenWarped.nii.gz
antsxfm=$regdir/ald_mri_allen.xfm

aldmr=$regdir/${vivo}v_mri_allen_ald.nii.gz
alxfm=$regdir/ald_mri_allen.xfm

#affmask=$regdir/stroke_${vivo}v_mask_aff.nii.gz

updmr=$regdir/upd_mri_allen_ants.nii.gz
affmask=$regdir/upd_${vivo}v_stroke_mask.nii.gz

#f3dmask=$regdirfinal/stroke_mask_allen.nii.gz
f3dinvmask=$regdir/f3d_upd_${vivo}v_stroke_mask.nii.gz
f3dmask=$regdir/f3d_stroke_mask_allen.nii.gz

# Reg_F3d registration parameters 

# Bending energy
be=3e-3
# Spline distance
sx=-7 # 5 vox

f3dmr=$regdir/mr_allen_f3d.nii.gz
f3dcpp=$regdir/f3d_mr_allen_cpp.nii.gz


if [ "$grp" == "stroke" ]; then
	
	if [[ ! -f $regdir/${vivo}v_mri_allenWarped.nii.gz ]]; then

		printf "\n Performing affine registration \n"

		echo antsRegistrationMIRACL_MRI.sh -d 3 -f $allenref -m $reginmr -o $regdir/${vivo}v_mri_allen -n $thrds -t $trans -r $rad | tee $regdir/ants_reg.log
		antsRegistrationMIRACL_MRI.sh -d 3 -f $allenref -m $reginmr -o $regdir/${vivo}v_mri_allen -n $thrds -t $trans -r $rad | tee $regdir/ants_reg.log

	fi

	if [[ ! -f $updmr ]]; then

		printf "\n Applying affine transformation to MRI \n"

		echo antsApplyTransforms -r $allenref -i $reginmr -n Bspline -t $regdir/${vivo}v_mri_allen0GenericAffine.mat -o $updmr
		antsApplyTransforms -r $allenref -i $reginmr -n Bspline -t $regdir/${vivo}v_mri_allen0GenericAffine.mat -o $updmr

	fi

	if [[ ! -f $affmask ]]; then

		printf "\n Applying affine transformation to stroke mask \n"		
		
		echo antsApplyTransforms -r $allenref -i $regmask -n MultiLabel -t $regdir/${vivo}v_mri_allen0GenericAffine.mat -o $affmask
		antsApplyTransforms -r $allenref -i $regmask -n MultiLabel -t $regdir/${vivo}v_mri_allen0GenericAffine.mat -o $affmask

	fi

	if [[ ! -f $f3dmr ]]; then

		printf "\n Performing non-rigmid registration \n"

		echo reg_f3d -ref $allenref -flo $updmr -cpp $f3dcpp -res $f3dmr -vel -sx $x -be $be -fmask $affmask | tee $regdir/f3d_reg.log
		reg_f3d -ref $allenref -flo $updmr -cpp $f3dcpp -res $f3dmr -vel -sx $sx -be $be -fmask $affmask | tee $regdir/f3d_reg.log

	fi

	if [[ ! -f $f3dmask ]]; then

		printf "\n Warping stroke mask \n"
		
		# warp stroke mask to allen - for later analysis

		echo reg_resample -ref $allenref -flo $affmask -cpp $f3dcpp -res $f3dinvmask -inter 0
		reg_resample -ref $allenref -flo $affmask -cpp $f3dcpp -res $f3dinvmask -inter 0

		# invert to get stroke mask

		echo fslmaths $f3dinvmask -binv $f3dmask
		fslmaths $f3dinvmask -binv $f3dmask

	fi


else

	if [[ ! -f $regdir/${vivo}v_mri_allenWarped.nii.gz ]]; then
		
		printf "\n Performing affine registration \n"

		echo antsRegistrationMIRACL_MRI.sh -d 3 -f $allenref -m $reginmr -o $regdir/${vivo}v_mri_allen -n $thrds -t $trans -r $rad | tee $regdir/ants_reg.log
		antsRegistrationMIRACL_MRI.sh -d 3 -f $allenref -m $reginmr -o $regdir/${vivo}v_mri_allen -n $thrds -t $trans -r $rad | tee $regdir/ants_reg.log

	fi
	
	if [[ ! -f $updmr ]]; then	

		printf "\n Applying affine transformation \n"

		echo antsApplyTransforms -r $allenref -i $reginmr -n Bspline -t $regdir/${vivo}v_mri_allen0GenericAffine.mat -o $updmr
		antsApplyTransforms -r $allenref -i $reginmr -n Bspline -t $regdir/${vivo}v_mri_allen0GenericAffine.mat -o $updmr

	fi	

	if [[ ! -f $f3dmr ]]; then	

		printf "\n Performing non-rigmid registration \n"

		echo reg_f3d -ref $allenref -flo $updmr -cpp $f3dcpp -res $f3dmr -vel -sx $sx  | tee $regdir/f3d_reg.log
		reg_f3d -ref $allenref -flo $updmr -cpp $f3dcpp -res $f3dmr -vel -sx $sx  | tee $regdir/f3d_reg.log

	fi

fi

# upsample output

resmr=$regdirfinal/${vivo}v_mri_allen.nii.gz 

if [[ ! -f $resmr ]]; then

	printf "\n Upsampling MRI output \n"

	echo mri_convert $f3dmr $resmr -vs 0.025 0.025 0.025 -rt Cubic
	mri_convert $f3dmr $resmr -vs 0.025 0.025 0.025 -rt Cubic

fi

# # smooth mr

# resmrsm=$regdirfinal/${vivo}v_mri_allen.nii.gz 

# if [[ ! -f $resmrsm ]]; then

# 	printf "\n Guassian smooth upsampled MRI output \n"

# 	echo c3d $resmr -smooth 0.075mm $resmrsm	
# 	c3d $resmr -smooth 0.075mm $resmrsm

# fi


if [[ ! -f $masked_mask ]]; then
	
	# mask 'stroke mask' with Allen to remove outer regions 
	allen_mask=$atlasdir/allen/allen_atlas_mask_res0.05.nii.gz
	masked_mask=$regdir/f3d_stroke_mask_allen_masked.nii.gz

	echo fslmaths $f3dmask -mas $allen_mask $masked_mask
	fslmaths $f3dmask -mas $allen_mask $masked_mask

fi


if [[ ! -f $eroded_mask ]]; then
	
	# erode mask by one vox
	eroded_mask=$regdir/f3d_stroke_mask_allen_masked_ero.nii.gz

	echo fslmaths $masked_mask -kernel boxv 1 -ero $eroded_mask
	fslmaths $masked_mask -kernel boxv 1 -ero $eroded_mask

fi


if [[ ! -f $final_mask ]]; then

	# convert to float 32
	final_mask=$regdirfinal/stroke_mask_allen.nii.gz
	
	echo c3d $eroded_mask -type float $final_mask
	c3d $eroded_mask -type float $final_mask

fi


#view results
# freeview $orgallen $resmr &

END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Registration done in $DIFF minutes. Have a good day!"