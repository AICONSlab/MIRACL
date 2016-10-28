#!/bin/bash

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

	1) Registers CLARITY data (down-sampled images) to Allen mouse brain atlas 
	2) Warps Allen annotations to the original high-res CLARITY space
	3) Warps the higher-resolution CLARITY to Allen space


	Usage: `basename $0`

	A GUI will open to choose your:

		- < Input down-sampled clarity nifti > : Preferably auto-fluorescence channel data (or Thy1_EYFP if no auto chan) 

		&

		- < Higher resolution clarity nifti > : Thy1_EYFP channel data 


	----------

	For command-line / scripting


	Usage: `basename $0` -i <input_down-sampled_clarity_nifti> -r <higher_res_clarity_nifti>

	Example: `basename $0` -i Reference_channel_5x_downsampled.nii.gz -r Thy1_channel_3x_downsampled.nii.gz

		arguments (required):

			i. Input down-sampled clarity nifti 

			r. Higher resolution clarity nifti

		optional arguments:
		
			m. Labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
				accepted inputs are: <split> or <combined>  (default: split)

			v. Voxel size/Resolutin of labels in um 
				accepted inputs are: 10, 25 or 50  (default: 10)
				
			l. image of input Allen Labels to warp (default: annotation_hemi_split_10um.nii.gz - which are at a resolution of 0.01mm/10um) 
				could be at a different depth than default labels 				

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

# Init atlas dir

atlasdir=${MIRACL_HOME}/atlases


# GUI for CLARITY input imgs

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	python ${MIRACL_HOME}/io/python_file_folder_gui.pyc -f file -s "$openstr" 
	
	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:r:l:m:v:" opt; do
    
	    case "${opt}" in

	        i)
            	inclar=${OPTARG}
            	;;
        	
        	r)
            	hresclar=${OPTARG}
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

	if [ -z ${inclar} ];
	then
		usage
		echo "ERROR: < -i => input clarity nii> not specified"
		exit 1
	fi


	if [ -z ${hresclar} ];
	then
		usage
		echo "ERROR: < -r => high-res clarity nii> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "Down-sampled auto-fluorescence (or Thy1) channel (nii/nii.gz)" inclar

	choose_file_gui "Higher resolution Thy1 channel (nii/nii.gz)" hresclar

	
	# check required input arguments

	if [ -z ${inclar} ];
	then
		usage
		echo "ERROR: <input clarity nii> was not chosen"
		exit 1
	fi


	if [ -z ${hresclar} ];
	then
		usage
		echo "ERROR: <high-res clarity nii> was not chosen"
		exit 1
	fi

fi


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

exec > >(tee -i ${regdir}/clar_allen_script.log)
exec 2>&1


#---------------------------
#---------------------------



# 1) Process clarity Functions

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


# resample to 0.05mm voxel size

function resampleclar()
{

	local inclar=$1
	local vox=$2
	local ifspacing=$3
	local interp=$4
	local resclar=$5
	
	ifdsntexistrun $resclar "Resmapling CLARITY input" ResampleImage 3 $inclar $resclar ${vox}x${vox}x${vox} $ifspacing $interp

	c3d $resclar -type short -o $resclar

}


# N4 bias correct

function biasfieldcorr()
{
	
	local resclar=$1
	local biasclar=$2	

	ifdsntexistrun $biasclar "Bias-correcting CLARITY image with N4" N4BiasFieldCorrection -d 3 -i $resclar -s 2 -o $biasclar

}


# Remove outline w erosion & dilation

# Thr

function thresh()
{

	local biasclar=$1
	local p1=$2  
	local p2=$3
	local t1=$4
	local t2=$5
	local thrclar=$6	

	ifdsntexistrun $thrclar "Thresholding CLARITY image" c3d $biasclar -threshold ${p1}% ${p2}% $t1 $t2 -o $thrclar	

}


# Ero

function erode()
{
	
	local thrclar=$1
	local erorad=$2
	local eromask=$3	

	ifdsntexistrun $eromask "Eroding CLARITY mask" ImageMath 3 $eromask ME $thrclar $erorad

}


# Dil

function dilate()
{
	
	local eromask=$1
	local dilrad=$2
	local dilmask=$3

	ifdsntexistrun $dilmask "Dilating CLARITY mask" ImageMath 3 $dilmask MD $eromask $dilrad

}


# mask

function maskimage()
{
		
	local biasclar=$1
	local dilmask=$2
	local betclar=$3
		
	ifdsntexistrun $betclar "Removing CLARITY image outline artifacts" MultiplyImages 3 $biasclar $dilmask $betclar

	c3d $betclar -type short -o $betclar

}


# Orient 

function orientimg()
{

	local betclar=$1
	local orttag=$2
	local ortint=$3
	local orttype=$4
	local ortclar=$5

	ifdsntexistrun $ortclar "Orienting CLARITY to standard orientation" \
	c3d $betclar -orient $orttag -interpolation $ortint -type $orttype -o $ortclar

}


# Smooth image

function smoothimg()
{
	
	local ortclar=$1
	local sigma=$2
	local smclar=$3

	ifdsntexistrun $smclar "Smoothing CLARITY image" SmoothImage 3 $ortclar 1 $smclar 0 1

	c3d $smclar -type short -o $smclar

}


# Crop to smallest roi

function croptosmall()
{
	
	local smclar=$1
	local trim=$2
	local clarroi=$3

	ifdsntexistrun $clarroi "Cropping CLARITY image to smallest ROI" c3d $smclar -trim ${trim}vox -type short -o $clarroi

}


#---------------------------


# 2a) initialize registration Function

function initclarallenreg()
{

	# Init imgs
	clarroi=$1
	allenref=$2

	# Init tform
	initform=$3

	# Init parms
	deg=$4
	radfrac=$5
	useprincax=$6
	localiter=$7
	
	# Out imgs
	initallen=$8


	# Init reg
	ifdsntexistrun $initform "Initializing registration ..." \
	 antsAffineInitializer 3 $clarroi $allenref $initform $deg $radfrac $useprincax $localiter


	# Warp Allen
	ifdsntexistrun $initallen "initializing Allen template" antsApplyTransforms -i $allenref -r $smclar -t $initform -o $initallen


}



#---------------------------


# 2b) Register to Allen atlas Function

function regclarallen()
{

	# Reg inputs
	local clarroi=$1
	local initallen=$2

	# Reg parms
	local trans=$3	
	local spldist=$4	
	local rad=$5	
	local prec=$6	
	local thrds=$7

	# Reg out
	local antsallen=$8

	# Perform ANTs registration between CLARITY and Allen atlas

	ifdsntexistrun $antsallen "Registering CLARITY data to allen atlas ... this will take a while" \
	antsRegistrationMIRACL.sh -d 3 -f $clarroi -m $initallen -o $regdir/allen_clar_ants -t $trans -p $prec -n $thrds -s $spldist -r $rad | tee $regdir/ants_reg.log


}


#---------------------------


# 3) Warp Allen labels to original CLARITY Function


function warpallenlbls()
{
	
	# In imgs
	local smclar=$1
	local lbls=$2

	# In tforms
	local antswarp=$3
	local antsaff=$4
	local initform=$5

	# Out lbls
	local wrplbls=$6
	
	# Ort pars
	local orttaglbls=$7
	local ortintlbls=$8
	local orttypelbls=$9
	local ortlbls=${10}

	# swap lbls
	local swplbls=${11}
	local tiflbls=${12}
	
	# Up lbls
    local hresclar=${13}
    local reslbls=${14}
    local restif=${15}


	# warp to registered clarity
	ifdsntexistrun $wrplbls "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r $smclar -i $lbls -n Multilabel -t $antswarp $antsaff $initform -o $wrplbls


	# orient to org 
	orientimg $wrplbls $orttaglbls $ortintlbls $orttypelbls $ortlbls

	# swap dim (x=>y / y=>x)
	ifdsntexistrun $swplbls "Swapping label dimensions" PermuteFlipImageOrientationAxes  3 $ortlbls $swplbls  1 0 2  0 0 0

	# create tif lbls
	ifdsntexistrun $tiflbls "Converting lbls to tif" c3d $swplbls -type $orttypelbls -o $tiflbls 

	# upsample to img dimensions

	# # get img dim
	 alldim=`PrintHeader $hresclar 2`

	 x=${alldim%%x*};
	 yz=${alldim#*x}; y=${yz%x*} ;
	 z=${alldim##*x};

	 dim="${x}x${y}x${z}";

	 ifdsntexistrun $reslbls "Upsampling labels to CLARITY resolution" \
	  c3d $swplbls -resample $dim -interpolation $ortintlbls -type $orttypelbls -o $reslbls
	# Can also resample with cubic (assuming 'fuzzy' lbls) or smooth resampled labels (c3d split) ... but > 700 lbls

    # create hres tif lbls
	ifdsntexistrun $restif "Converting high res lbls to tif" c3d $reslbls -type $orttypelbls -o $restif


}


#---------------------------


# 4) Warp down 3x CLARITY (high res) to Allen Function


function warphresclarallen()
{

	# Ort clar
	local hresclar=$1
	local ortclartag=$2
	local ortclarint=$3
	local ortclartype=$4
	local orthresclar=$5

	# Reg to allen
	local allenhres=$6
	local initform=$7
	local antsaff=$8	
	local antsinvwarp=$9
	
	local regorgclar=${10}


	# Orient channel to std
	orientimg $hresclar $ortclartag $ortclarint $ortclartype $orthresclar

	# Apply warps
	ifdsntexistrun $regorgclar "Applying ants deformation to high-res CLARITY" \
	antsApplyTransforms -r $allenhres -i $orthresclar -n Bspline -t [${initform},1] [${antsaff},1] ${antsinvwarp} -o $regorgclar --float

}


#---------------------------
#---------------------------



# Build main function

function main()
{

# 1) Process clarity

	# resample to 0.05mm voxel 
	resclar=$regdir/clar_res0.05.nii.gz

	resampleclar $inclar 0.05 0 4 $resclar


	# N4 bias correct
	biasclar=$regdir/clar_res0.05_bias.nii.gz

	biasfieldcorr $resclar $biasclar


	# Remove outline w erosion & dilation
	
	# Thr
	thrclar=$regdir/clar_res0.05_bias_thr.nii.gz

	thresh $biasclar 2 50 0 1 $thrclar


	# Ero
	eromask=$regdir/clar_res0.05_ero_mask.nii.gz

	erode $thrclar 12 $eromask


	# Dil
	dilmask=$regdir/clar_res0.05_dil_mask.nii.gz

	dilate $eromask 9 $dilmask


	# Mask
	betclar=$regdir/clar_res0.05_bias_bet.nii.gz

	maskimage $biasclar $dilmask $betclar


	# Orient
	ortclar=$regdir/clar_res0.05_ort.nii.gz

	orientimg $betclar ALS Cubic short $ortclar


	# Smooth
	smclar=$regdir/clar_res0.05_ort_sm.nii.gz

	smoothimg $ortclar 1 $smclar

	
	# Crop to smallest roi
	clarroi=$regdir/clar_res0.05_ort_sm_roi.nii.gz

	croptosmall $smclar 5 $clarroi	
	

	# make clarity link
	clarlnk=$regdir/clar.nii.gz

	if [[ ! -f $clarlnk ]]; then ln -s $smclar $clarlnk ; fi


	#---------------------------


# 2a) initialize registration

	# Allen atlas template
	allenref=$atlasdir/aba/template/average_template_25um.nii.gz

	initform=$regdir/init_tform.mat 

	# Init parms

	deg=2 # search increment in degrees 
	radfrac=0.05 # arc around principal axis
	useprincax=0 # rotation searched around principal axis
	localiter=100 # num of iteration for optimization at search point

	# Out Allen
	initallen=$regdir/init_allen.nii.gz


	initclarallenreg $clarroi $allenref $initform $deg $radfrac $useprincax $localiter $initallen


	#---------------------------


# 2b) Register to Allen atlas
	

	# Parameters: 

	# transform
	trans=b #Bspline Syn
	# spline distance 26 
	spldist=26
	# cross correlation radius
	rad=2
	# precision 
	prec=f # float
	# get num of threads 
	thrds=`nproc`

	# Out Allen
	antsallen=$regdir/allen_clar_antsWarped.nii.gz


	regclarallen $clarroi $initallen $trans $spldist $rad $prec $thrds $antsallen


	#---------------------------


# 3) Warp Allen labels to original CLARITY (down sampled 2x)


	# Tforms
	antswarp=$regdir/allen_clar_ants1Warp.nii.gz
	antsaff=$regdir/allen_clar_ants0GenericAffine.mat

	# If want to warp multi-res / hemi lbls
	
	if [[ -z $lbls ]]; then
		
		if [[ -z $hemi ]]; then
			
			hemi=split

		fi

		if [[ -z $vox ]]; then
			
			vox=10

		fi

		lbls=$atlasdir/aba/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz
	fi

	base=`basename $lbls`
	lblsname=${base%%.*};

	# Out lbls
	wrplbls=$regdir/${lblsname}_ants.nii.gz
	ortlbls=$regdir/${lblsname}_ants_ort.nii.gz
	swplbls=$regdir/${lblsname}_ants_swp.nii.gz
	tiflbls=$regdir/${lblsname}_ants.tif
	reslbls=$regdirfinal/allen_lbls_clar_ants.nii.gz
	restif=$regdirfinal/allen_lbls_clar_ants.tif

	# upsample in python now
	# warpallenlbls $smclar $lbls $antswarp $antsaff $initform $wrplbls LPI NearestNeighbor short $ortlbls $resclar $reslbls

	warpallenlbls $smclar $lbls $antswarp $antsaff $initform $wrplbls RPI NearestNeighbor short $ortlbls $swplbls $tiflbls $hresclar $reslbls $restif

	#---------------------------


# 4) Warp down 3x CLARITY (high res) to Allen


	# ort hres clar
	orthresclar=$regdir/hres_EYFP_ort.nii.gz
	
	# hres Allen
	allenhres=$atlasdir/aba/template/average_template_10um.nii.gz

	# ants inv warp
	antsinvwarp=$regdir/allen_clar_ants1InverseWarp.nii.gz

	# out warp hres clar
	regorgclar=$regdirfinal/hresclar_allen_ants.nii.gz


	warphresclarallen $hresclar ALS Cubic short $orthresclar $allenhres $initform $antsaff $antsinvwarp $regorgclar

}


#--------------------


# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Registration and Allen label warping done in $DIFF minutes. Have a good day!"