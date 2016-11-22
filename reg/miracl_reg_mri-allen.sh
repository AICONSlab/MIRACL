#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/init/version_num.txt`
	printf "MIRACL pipeline v. $ver \n"
}

# TODOHp: add stroke mask later
# TODOlp: remove FSL/bet 

# help/usage function
function usage()
{
    
    cat <<usage

	1) Registers in-vivo or ex-vivo MRI data to Allen Reference mouse brain Atlas
	2) Warps Allen annotations to the MRI space


	Usage: `basename $0`

	A GUI will open to choose your:

		- < Input MRI nifti > : Preferably T2-weighted

	----------

	For command-line / scripting


	Usage: `basename $0` -i <invivo_or_exvivo> mri

	Example: `basename $0` -i inv_mri.nii.gz

		arguments (required):

			i. Input MRI nifti

		optional arguments:
		
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

		- FSL


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


if [ -z ${ANTSPATH} ];
then
	printf "\n ERROR: ANTS not initialized .. please install it & rerun script \n"
	exit 1
else 
	printf "\n ANTS path check: OK... \n" 
fi

fslcmd=`which fsl`

if [ -z "${fslcmd// }" ];
then
	echo "ERROR: < FSL not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
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

# Init atlas dir

atlasdir=${MIRACL_HOME}/atlases


# GUI for MRI input imgs

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	${MIRACL_HOME}/io/python_file_folder_gui.py -f file -s "$openstr"
	
	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:l:m:v:" opt; do
    
	    case "${opt}" in

	        i)
            	inmr=${OPTARG}
            	;;
        	
        	l)
            	lbls=${OPTARG}
            	;;

        	m)
            	hemi=${OPTARG}
            	;;
        	v)
            	vox=${OPTARG}
            	;;
        	*)
            	usage            	
            	;;

		esac
	
	done    	


	# check required input arguments

	if [ -z ${inmr} ];
	then
		usage
		echo "ERROR: < -i => input MRI nii> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "In-vivo or Ex-vivo MRI (nii/nii.gz)" inmr

	# check required input arguments

	if [ -z ${inmr} ];
	then
		usage
		echo "ERROR: <input MRI nii> was not chosen"
		exit 1
	fi

fi


# get time

START=$(date +%s)


# make reg dir

regdirfinal=$PWD/reg_final
regdir=$PWD/mri_allen_reg


if [[ ! -d $regdir ]]; then

	printf "\n Creating registration folder\n"
	mkdir -p $regdirfinal $regdir

fi

# output log file of script

exec > >(tee -i ${regdir}/mri_allen_script.log)
exec 2>&1


#---------------------------
#---------------------------



# 1) Process MRI Functions

# Function to check if file exists then runs other command

function ifdsntexistrun() 
{  

	local outfile="$1"; 
	local outstr="$2"; 
	local fun="${@:3}";  

	if [[ ! -f $outfile ]]; then 

		printf "\n $outstr \n"; 
		echo "$fun"; 
		eval "$fun"; 

	else  
		
		printf "\n $outfile already exists ... skipping \n"; 

	fi ; 

}


# N4 bias correct

function biasfieldcorr()
{
	
	local unbiasmr=$1
	local biasmr=$2	

	ifdsntexistrun ${biasmr} "Bias-correcting MRI image with N4" N4BiasFieldCorrection -d 3 -i ${unbiasmr} -s 2 -o ${biasmr}

}

# Remove outline w erosion & dilation

# Thr

function thresh()
{

	local biasmr=$1
	local thr=$2
	local thrmr=$3

#	ifdsntexistrun $thrmr "Thresholding MRI image" c3d $biasmr -threshold ${p1}% ${p2}% $t1 $t2 -o $thrmr
    ifdsntexistrun ${thrmr} "Thresholding MRI image" fslmaths $biasmr -thrP ${thr} ${thrmr}

}

# Crop to smallest roi

function croptosmall()
{

	local thrmr=$1
	local cropmr=$2

    dims=`fslstats ${thrmr} -w`

#	ifdsntexistrun ${cropmr} "Cropping MRI image to smallest ROI" c3d $smmr -trim ${trim}vox -type short -o $mrroi
    ifdsntexistrun ${cropmr} "Cropping MRI image to smallest ROI" fslroi ${thrmr} ${cropmr} ${dims}

}

## Ero
#
#function erode()
#{
#
#	local thrmr=$1
#	local erorad=$2
#	local eromask=$3
#
#	ifdsntexistrun $eromask "Eroding MRI mask" ImageMath 3 $eromask ME $thrmr $erorad
#
#}
#
#
## Dil
#
#function dilate()
#{
#
#	local eromask=$1
#	local dilrad=$2
#	local dilmask=$3
#
#	ifdsntexistrun $dilmask "Dilating MRI mask" ImageMath 3 $dilmask MD $eromask $dilrad
#
#}

# change header * 10 dims

function mulheader()
{

	local unhdmr=$1
	local mulfac=$2
	local hdmr=$3

	dim1=`fslinfo ${unhdmr} | grep pixdim1`; x=${dim##*1 } ;
	dim2=`fslinfo ${unhdmr} | grep pixdim2`; y=${dim##*2 } ;
	dim3=`fslinfo ${unhdmr} | grep pixdim3`; z=${dim##*3 } ;

    nx=`echo ${x}*${mulfac} | bc` ;
    ny=`echo ${y}*${mulfac} | bc` ;
    nz=`echo ${z}*${mulfac} | bc` ;

    ifdsntexistrun ${hdmr} "Altering MRI header" c3d ${unhdmr} -spacing ${x}x${y}x${z}mm ${hdmr}

}

# skull strip

function skullstrip()
{

	local skullmr=$1
	local betmr=$2

    com=`fslstats ${skullmr} -C`

    ifdsntexistrun ${betmr} "Skull stripping MRI image" bet ${skullmr} ${betmr} -r 55 -c $com -f 0.3

}

## mask
#
#function maskimage()
#{
#
#	local biasmr=$1
#	local dilmask=$2
#	local betmr=$3
#
#	ifdsntexistrun $betmr "Removing MRI image outline artifacts" MultiplyImages 3 $biasmr $dilmask $betmr
#
#	c3d $betmr -type short -o $betmr
#
#}


# Orient 

function orientimg()
{

	local unortmr=$1
	local orttag=$2
	local ortint=$3
	local orttype=$4
	local ortmr=$5

	ifdsntexistrun ${ortmr} "Orienting MRI to standard orientation" \
	c3d ${unortmr} -orient ${orttag} -interpolation ${ortint} -type ${orttype} -o ${ortmr}

}


## Smooth image
#
#function smoothimg()
#{
#
#	local ortmr=$1
#	local sigma=$2
#	local smmr=$3
#
#	ifdsntexistrun $smmr "Smoothing MRI image" SmoothImage 3 $ortmr 1 $smmr 0 1
#
#	c3d $smmr -type short -o $smmr
#
#}


#---------------------------

# 2) Register to Allen atlas Function

function regmrallen()
{

	# Reg inputs
	local mrprereg=$1
	local allen=$2

	# Reg parms
	local trans=$3	
	local spldist=$4	
	local rad=$5	
	local prec=$6	
	local thrds=$7

	# Reg out
	local antsallen=$8

    # convert init allen into int
    c3d ${initallen} -type int -o ${initallen}

	# Perform ANTs registration between MRI and Allen atlas

	ifdsntexistrun $antsallen "Registering MRI data to allen atlas ... this will take a while" \
	antsRegistrationMIRACL_MRI.sh -d 3 -f ${mrprereg} -m ${allen} -o ${regdir}/allen_mr_ants -t ${trans} -p ${prec} -n ${thrds} -s ${spldist} -r ${rad} | tee ${regdir}/ants_reg.log


}


#---------------------------


# 3) Warp Allen labels to original MRI Function


#function warpallenlbls()
#{
#
#	# In imgs
#	local smmr=$1
#	local lbls=$2
#
#	# In tforms
#	local antswarp=$3
#	local antsaff=$4
#	local initform=$5
#
#	# Out lbls
#	local wrplbls=$6
#
#	# Ort pars
#	local orttaglbls=$7
#	local ortintlbls=$8
#	local orttypelbls=$9
#	local ortlbls=${10}
#
#	# swap lbls
#	local swplbls=${11}
#	local tiflbls=${12}
#
#	# Up lbls
#    local inmr=${13}
#    local reslbls=${14}
#    local restif=${15}
#
#	# warp to registered MRI
#	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
#	 antsApplyTransforms -r ${smmr} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff} ${initform} -o ${wrplbls}
#
#	# orient to org
#	orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}
#
#	# swap dim (x=>y / y=>x)
#	ifdsntexistrun ${swplbls} "Swapping label dimensions" PermuteFlipImageOrientationAxes  3 ${ortlbls} ${swplbls}  1 0 2  0 0 0
#
#	# create tif lbls
#	ifdsntexistrun ${tiflbls} "Converting lbls to tif" c3d ${swplbls} -type ${orttypelbls} -o ${tiflbls}
#
#	# upsample to img dimensions
#
#	# # get img dim
#	alldim=`PrintHeader ${inmr} 2`
#    x=${alldim%%x*};
#	yz=${alldim#*x}; y=${yz%x*} ;
#	z=${alldim##*x};
#
#    downfactor=`echo ${inmr} | egrep -o "[0-9]{2}x_down" | egrep -o "[0-9]{2}"`
#
#    xu=$((${x}*${downfactor}));
#    yu=$((${y}*${downfactor}));
#
#    # get dims from hres tif
##    tif=
##    dims=`c3d ${tif} -info-full | grep Dimensions`
##    nums=${dims##*[}; x=${nums%%,*}; xy=${nums%,*}; y=${xy##*,};
##    alldim=`PrintHeader ${inmr} 2` ;  z=${alldim##*x};
#
#	dim="${yu}x${xu}x${z}"; # inmr diff orientation need to swap x/y
#
#	ifdsntexistrun ${reslbls} "Upsampling labels to MRI resolution" \
#	c3d ${swplbls} -resample ${dim} -interpolation $ortintlbls -type ${orttypelbls} -o ${reslbls}
##	  Can also resample with cubic (assuming 'fuzzy' lbls) or smooth resampled labels (c3d split) ... but > 700 lbls
#
##     create hres tif lbls
#	ifdsntexistrun ${restif} "Converting high res lbls to tif" c3d ${reslbls} -type ${orttypelbls} -o ${restif}
#
#
#}
#

#---------------------------


# Build main function

function main()
{

# 1) Process MRI

	# N4 bias correct
	biasmr=${regdir}/mr_bias.nii.gz
	biasfieldcorr ${inmr} ${biasmr}

	# Thr
	thrmr=${regdir}/mr_bias_thr.nii.gz
	thresh ${biasmr} 40 ${thrmr}

    # Crop to smallest roi
	mrroi=${regdir}/mr_bias_thr_roi.nii.gz
	croptosmall ${thrmr} ${mrroi}

    # Change header * 10 dims
    hdmr=${regdir}/mr_bias_thr_roi_hd.nii.gz
    mulheader ${mrroi} 10 ${hdmr}

    # Skull strip
    betmr=${regdir}/mr_bet.nii.gz
    skullstrip ${hdmr} ${betmr}

#	# Ero (remove any components attached to the brain)
#	eromask=${regdir}/mr_ero_mask.nii.gz
#	erode ${thrmr} 3 ${eromask}
#
#    # Get largest component
#    conncomp=${regdir}/mr_ero_mask_comp.nii.gz
#    c3d ${eromask} -comp -threshold 1 1 1 0 -o ${conncomp}
#
#	# Dil
#	dilmask=${regdir}/mr_dil_mask.nii.gz
#	dilate ${conncomp} 3 ${dilmask}
#
#	# Mask
#	betmr=${regdir}/mr_bias_bet.nii.gz
#	maskimage ${biasmr} ${dilmask} ${betmr}

    # TODOlp: ask for certain orientation

	# Orient
	ortmr=${regdir}/mr_ort.nii.gz
	orientimg ${betmr} RAI Cubic short ${ortmr}

    # Update back header
    orghdmr=${regdir}/mr_bias_thr_roi_hd.nii.gz
    mulheader ${ortmr} 0.1 ${orghdmr}

#	# Smooth
#	smmr=${regdir}/mr_ort_sm.nii.gz
#	smoothimg ${ortmr} 1 ${smmr}

	# make MRI copy
	mrlnk=${regdir}/mr.nii.gz
	if [[ ! -f ${mrlnk} ]]; then cp ${orghdmr} ${mrlnk} ; fi

	#---------------------------

# 2) Register to Allen atlas
	

	# Parameters: 

	# transform
	trans=b #Bspline Syn
	# spline distance 26 
	spldist=26
	# cross correlation radius
	rad=8
	# precision 
	prec=d # double precision (otherwise ITK error in some cases!)
	# get num of threads 
	thrds=`nproc`

    # Allen atlas template
	allenref=$atlasdir/ara/template/average_template_25um.nii.gz

	# Out Allen
	antsallen=$regdir/allen_mr_antsWarped.nii.gz


	regmrallen ${orghdmr} ${allenref} ${trans} ${spldist} ${rad} ${prec} ${thrds} ${antsallen}


	#---------------------------


# 3) Warp Allen labels to original MRI (down sampled 2x)


#	# Tforms
#	antswarp=$regdir/allen_mr_ants1Warp.nii.gz
#	antsaff=$regdir/allen_mr_ants0GenericAffine.mat
#
#	# If want to warp multi-res / hemi lbls
#
#	if [[ -z $lbls ]]; then
#
#		if [[ -z $hemi ]]; then
#
#			hemi=split
#
#		fi
#
#		if [[ -z $vox ]]; then
#
#			vox=10
#
#		fi
#        lbls=$atlasdir/ara/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz
#
#	fi
#
#	base=`basename $lbls`
#	lblsname=${base%%.*};
#
#	# Out lbls
#	wrplbls=${regdir}/${lblsname}_ants.nii.gz
#	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
#	swplbls=${regdir}/${lblsname}_ants_swp.nii.gz
#	tiflbls=${regdir}/${lblsname}_ants.tif
#	reslbls=${regdirfinal}/allen_lbls_mr_ants.nii.gz
#	restif=${regdirfinal}/allen_lbls_mr_ants.tif
#
#	# upsample in python now
#	# warpallenlbls $smmr $lbls $antswarp $antsaff $initform $wrplbls LPI NearestNeighbor short $ortlbls $resmr $reslbls
#
#
#	warpallenlbls ${smmr} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} RPI NearestNeighbor short ${ortlbls} ${swplbls} ${tiflbls} ${inmr} ${reslbls} ${restif}


#--------------------


# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Registration and Allen label warping done in $DIFF minutes. Have a good day!"