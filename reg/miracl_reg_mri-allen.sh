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

	ifdsntexistrun $biasmr "Bias-correcting MRI image with N4" N4BiasFieldCorrection -d 3 -i $resmr -s 2 -o $biasmr

}


# resample to 0.05mm voxel size

function resamplemr()
{

	local inmr=$1
	local vox=$2
	local ifspacing=$3
	local interp=$4
	local resmr=$5
	
	ifdsntexistrun $resmr "Resmapling MRI input" ResampleImage 3 $inmr $resmr ${vox}x${vox}x${vox} $ifspacing $interp

	c3d $resmr -type short -o $resmr

}





# Remove outline w erosion & dilation

# Thr

function thresh()
{

	local biasmr=$1
	local p1=$2  
	local p2=$3
	local t1=$4
	local t2=$5
	local thrmr=$6	

	ifdsntexistrun $thrmr "Thresholding MRI image" c3d $biasmr -threshold ${p1}% ${p2}% $t1 $t2 -o $thrmr	

}


# Ero

function erode()
{
	
	local thrmr=$1
	local erorad=$2
	local eromask=$3	

	ifdsntexistrun $eromask "Eroding MRI mask" ImageMath 3 $eromask ME $thrmr $erorad

}


# Dil

function dilate()
{
	
	local eromask=$1
	local dilrad=$2
	local dilmask=$3

	ifdsntexistrun $dilmask "Dilating MRI mask" ImageMath 3 $dilmask MD $eromask $dilrad

}


# mask

function maskimage()
{
		
	local biasmr=$1
	local dilmask=$2
	local betmr=$3
		
	ifdsntexistrun $betmr "Removing MRI image outline artifacts" MultiplyImages 3 $biasmr $dilmask $betmr

	c3d $betmr -type short -o $betmr

}


# Orient 

function orientimg()
{

	local betmr=$1
	local orttag=$2
	local ortint=$3
	local orttype=$4
	local ortmr=$5

	ifdsntexistrun $ortmr "Orienting MRI to standard orientation" \
	c3d $betmr -orient $orttag -interpolation $ortint -type $orttype -o $ortmr

}


# Smooth image

function smoothimg()
{
	
	local ortmr=$1
	local sigma=$2
	local smmr=$3

	ifdsntexistrun $smmr "Smoothing MRI image" SmoothImage 3 $ortmr 1 $smmr 0 1

	c3d $smmr -type short -o $smmr

}


# Crop to smallest roi

function croptosmall()
{
	
	local smmr=$1
	local trim=$2
	local mrroi=$3

	ifdsntexistrun $mrroi "Cropping MRI image to smallest ROI" c3d $smmr -trim ${trim}vox -type short -o $mrroi

}


#---------------------------


# 2a) initialize registration Function

function initmrallenreg()
{

	# Init imgs
	mrroi=$1
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
	 antsAffineInitializer 3 $mrroi $allenref $initform $deg $radfrac $useprincax $localiter


	# Warp Allen
	ifdsntexistrun $initallen "initializing Allen template" antsApplyTransforms -i $allenref -r $smmr -t $initform -o $initallen


}



#---------------------------


# 2b) Register to Allen atlas Function

function regmrallen()
{

	# Reg inputs
	local mrroi=$1
	local initallen=$2

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
	antsRegistrationMIRACL.sh -d 3 -f $mrroi -m $initallen -o $regdir/allen_mr_ants -t $trans -p $prec -n $thrds -s $spldist -r $rad | tee $regdir/ants_reg.log


}


#---------------------------


# 3) Warp Allen labels to original MRI Function


function warpallenlbls()
{
	
	# In imgs
	local smmr=$1
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
    local inmr=${13}
    local reslbls=${14}
    local restif=${15}

	# warp to registered MRI
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${smmr} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff} ${initform} -o ${wrplbls}

	# orient to org 
	orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}

	# swap dim (x=>y / y=>x)
	ifdsntexistrun ${swplbls} "Swapping label dimensions" PermuteFlipImageOrientationAxes  3 ${ortlbls} ${swplbls}  1 0 2  0 0 0

	# create tif lbls
	ifdsntexistrun ${tiflbls} "Converting lbls to tif" c3d ${swplbls} -type ${orttypelbls} -o ${tiflbls}

	# upsample to img dimensions

	# # get img dim
	alldim=`PrintHeader ${inmr} 2`
    x=${alldim%%x*};
	yz=${alldim#*x}; y=${yz%x*} ;
	z=${alldim##*x};

    downfactor=`echo ${inmr} | egrep -o "[0-9]{2}x_down" | egrep -o "[0-9]{2}"`

    xu=$((${x}*${downfactor}));
    yu=$((${y}*${downfactor}));

    # get dims from hres tif
#    tif=
#    dims=`c3d ${tif} -info-full | grep Dimensions`
#    nums=${dims##*[}; x=${nums%%,*}; xy=${nums%,*}; y=${xy##*,};
#    alldim=`PrintHeader ${inmr} 2` ;  z=${alldim##*x};

	dim="${yu}x${xu}x${z}"; # inmr diff orientation need to swap x/y

# TODOhp : warp labels again to high res (make empty image w same dims?)
# TODOhp : remove this comment

#	ifdsntexistrun ${reslbls} "Upsampling labels to MRI resolution" \
#	c3d ${swplbls} -resample ${dim} -interpolation $ortintlbls -type ${orttypelbls} -o ${reslbls}
	 # Can also resample with cubic (assuming 'fuzzy' lbls) or smooth resampled labels (c3d split) ... but > 700 lbls

    # create hres tif lbls
#	ifdsntexistrun ${restif} "Converting high res lbls to tif" c3d ${reslbls} -type ${orttypelbls} -o ${restif}


}

#---------------------------

# 4a) Warp input MRI to Allen Function

function warpinmrallen()
{

	# Ort mr
	inmr=$1
	ortmrtag=$2
	ortmrint=$3
	ortmrtype=$4
	orthresmr=$5

	# Reg to allen
	allenhres=$6
	initform=$7
	antsaff=$8
	antsinvwarp=$9

	regorgmr=${10}

	# Orient channel to std
	orientimg ${inmr} ${ortmrtag} ${ortmrint} ${ortmrtype} ${orthresmr}

	# Apply warps
	ifdsntexistrun ${regorgmr} "Applying ants deformation to input MRI" \
	antsApplyTransforms -r ${allenhres} -i ${orthresmr} -n Bspline -t [${initform},1] [${antsaff},1] ${antsinvwarp} -o ${regorgmr} --float

}

#---------------------------

# 4b) Warp down 3x MRI (high res) to Allen Function


function warphresmrallen()
{

	# Ort mr
	hresmr=$1
	ortmrtag=$2
	ortmrint=$3
	ortmrtype=$4
	orthresmr=$5

	# Reg to allen
	allenhres=$6
	initform=$7
	antsaff=$8
	antsinvwarp=$9
	
	regorgmr=${10}

	# Orient channel to std
	orientimg ${hresmr} ${ortmrtag} ${ortmrint} ${ortmrtype} ${orthresmr}

	# Apply warps
	ifdsntexistrun $regorgmr "Applying ants deformation to high-res MRI" \
	antsApplyTransforms -r ${allenhres} -i ${orthresmr} -n Bspline -t [${initform},1] [${antsaff},1] ${antsinvwarp} -o ${regorgmr} --float

}


#---------------------------
#---------------------------



# Build main function

function main()
{

# 1) Process MRI


	# resample to 0.05mm voxel
	resmr=${regdir}/mr_res0.05.nii.gz
	resamplemr ${inmr} 0.05 0 4 ${resmr}

	# N4 bias correct
	biasmr=${regdir}/mr_res0.05_bias.nii.gz
	biasfieldcorr ${resmr} ${biasmr}

	# Remove outline w erosion & dilation

	# Thr
	thrmr=${regdir}/mr_res0.05_bias_thr.nii.gz
	thresh ${biasmr} 2 50 0 1 ${thrmr}

	# Ero (remove any components attached to the brain)
	eromask=${regdir}/mr_res0.05_ero_mask.nii.gz
	erode ${thrmr} 3 ${eromask}

    # Get largest component
    conncomp=${regdir}/mr_res0.05_ero_mask_comp.nii.gz
    c3d ${eromask} -comp -threshold 1 1 1 0 -o ${conncomp}

	# Dil
	dilmask=${regdir}/mr_res0.05_dil_mask.nii.gz
	dilate ${conncomp} 3 ${dilmask}

	# Mask
	betmr=${regdir}/mr_res0.05_bias_bet.nii.gz
	maskimage ${biasmr} ${dilmask} ${betmr}

	# Orient
	ortmr=${regdir}/mr_res0.05_ort.nii.gz
	orientimg ${betmr} ALS Cubic short ${ortmr}

	# Smooth
	smmr=${regdir}/mr_res0.05_ort_sm.nii.gz
	smoothimg ${ortmr} 1 ${smmr}

	# Crop to smallest roi
	mrroi=${regdir}/mr_res0.05_ort_sm_roi.nii.gz
	croptosmall ${smmr} 5 ${mrroi}

	# make MRI copy
	mrlnk=${regdir}/mr.nii.gz
	if [[ ! -f ${mrlnk} ]]; then cp ${smmr} ${mrlnk} ; fi

	#---------------------------


# 2a) initialize registration

	# Allen atlas template
	allenref=$atlasdir/ara/template/average_template_25um.nii.gz

	initform=$regdir/init_tform.mat 

	# Init parms

	deg=2 # search increment in degrees 
	radfrac=0.05 # arc around principal axis
	useprincax=0 # rotation searched around principal axis
	localiter=100 # num of iteration for optimization at search point

	# Out Allen
	initallen=$regdir/init_allen.nii.gz


	initmrallenreg $mrroi $allenref $initform $deg $radfrac $useprincax $localiter $initallen


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
	prec=d # double precision (otherwise ITK error in some cases!)
	# get num of threads 
	thrds=`nproc`

	# Out Allen
	antsallen=$regdir/allen_mr_antsWarped.nii.gz


	regmrallen $mrroi $initallen $trans $spldist $rad $prec $thrds $antsallen


	#---------------------------


# 3) Warp Allen labels to original MRI (down sampled 2x)


	# Tforms
	antswarp=$regdir/allen_mr_ants1Warp.nii.gz
	antsaff=$regdir/allen_mr_ants0GenericAffine.mat

	# If want to warp multi-res / hemi lbls
	
	if [[ -z $lbls ]]; then

		if [[ -z $hemi ]]; then
			
			hemi=split

		fi

		if [[ -z $vox ]]; then
			
			vox=10

		fi
        lbls=$atlasdir/ara/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz

	fi

	base=`basename $lbls`
	lblsname=${base%%.*};

	# Out lbls
	wrplbls=${regdir}/${lblsname}_ants.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
	swplbls=${regdir}/${lblsname}_ants_swp.nii.gz
	tiflbls=${regdir}/${lblsname}_ants.tif
	reslbls=${regdirfinal}/allen_lbls_mr_ants.nii.gz
	restif=${regdirfinal}/allen_lbls_mr_ants.tif

	# upsample in python now
	# warpallenlbls $smmr $lbls $antswarp $antsaff $initform $wrplbls LPI NearestNeighbor short $ortlbls $resmr $reslbls


	warpallenlbls ${smmr} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} RPI NearestNeighbor short ${ortlbls} ${swplbls} ${tiflbls} ${inmr} ${reslbls} ${restif}

	#---------------------------


# 4) Warp input MRI to Allen


	# ort hres mr
#	orthresmr=${regdir}/hres_EYFP_ort.nii.gz
	ortinmr=${regdir}/mr_ort.nii.gz

	# hres Allen
	allenhres=${atlasdir}/ara/template/average_template_10um.nii.gz

	# ants inv warp
	antsinvwarp=${regdir}/allen_mr_ants1InverseWarp.nii.gz

	# out warp hres mr
#	regorgmr=${regdirfinal}/hresmr_allen_ants.nii.gz
    regorgmr=${regdirfinal}/mr_allen_ants.nii.gz


    warpinmrallen ${inmr} ALS Cubic short ${ortinmr} $allenhres $initform $antsaff $antsinvwarp $regorgmr
#	warphresmrallen ${hresmr} ALS Cubic short ${orthresmr} $allenhres $initform $antsaff $antsinvwarp $regorgmr

}


#--------------------


# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Registration and Allen label warping done in $DIFF minutes. Have a good day!"