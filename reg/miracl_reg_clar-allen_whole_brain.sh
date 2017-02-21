#!/usr/bin/env bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version_num.txt`
	printf "\n MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{
    
    cat <<usage

	1) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
	2) Warps Allen annotations to the original high-res CLARITY space
	3) Warps the higher-resolution CLARITY to Allen space

	if no inputs are given function will run in GUI mode

	For command-line / scripting

	Usage: `basename $0` -i [ input clarity nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ]

    Example: `basename $0` -i Reference_channel_05x_down.nii.gz -o ARS -m combined -v 25

    arguments (required):

		i.  input down-sampled clarity nii
		    Preferably auto-fluorescence channel data (or Thy1_EYFP if no auto chan)

		    file name should have "##x_down" like "05x_down" (meaning 5x downsampled)  -> ex. stroke13_05x_down_Ref_chan.nii.gz
            [this should be accurate as it is used for allen label upsampling to clarity]

    optional arguments:

        o.  orient code (default: ALS)
            to orient nifti from original orientation to "standard/Allen" orientation
		
        m.  hemisphere mirror (default: combined)
            warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
			accepted inputs are: <split> or <combined>

        v.  labels voxel size/Resolution in um (default: 10)
			accepted inputs are: 10, 25 or 50
				
        l.  input Allen labels to warp (default: annotation_hemi_combined_10um.nii.gz )
			input labels could be at a different depth than default labels

			If l. is specified (m & v cannot be specified)


	----------

	Main Outputs


		reg_final/clar_allen_space.nii.gz: Clarity data in Allen reference space

        reg_final/clar_downsample_res(vox)um.nii.gz : Clarity data downsampled and oriented to "standard"

		reg_final/annotation_hemi_(hemi)_(vox)um_clar_downsample.nii.gz : Allen labels registered to downsampled Clarity

        reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif : Allen labels registered to oriented Clarity

        reg_final/annotation_hemi_(hemi)_(vox)um_clar.tif : Allen labels registered to original (full-resolution) Clarity


        - To visualize clarity data in Allen space - assuming chosen v/vox 10um
            from command line:

                itksnap -g \$allen10 -o reg_final/clar_allen_space.nii.gz -s \$lbls10 -l \$snaplut

            from GUI:

                \$allen10 = \$MIRACL_HOME/atlases/ara/template/average_template_10um.nii.gz -> (Main Image)

                \$lbls10 = \$MIRACL_HOME/atlases/ara/annotation/annotation_hemi_combined_10um.nii.gz -> (Segmentation)

                \$snaplut = \$MIRACL_HOME/atlases/ara/ara_snaplabels_lut.txt -> (Label Descriptions)


        - To visualize Allen labels in downsampled clarity data space (from command line):

            itksnap -g clar_downsample_res(vox)um.nii.gz -s reg_final/annotation_hemi_(hemi)_(vox)um_clar_downsample.nii.gz


        - Full resolution Allen labels in original clarity space (.tif) can be visualized by Fiji


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

    printf "\n ERROR: MIRACL not initialized .. please run init/setup_miracl.sh & rerun script \n"
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

# make reg dir

regdirfinal=$PWD/reg_final
regdir=$PWD/clar_allen_reg


if [[ ! -d ${regdir} ]]; then

	printf "\n Creating registration folder\n"
	mkdir -p ${regdirfinal} ${regdir}

fi

# output log file of script

exec > >(tee -i ${regdir}/clar_allen_script.log)
exec 2>&1


# Init atlas dir

atlasdir=${MIRACL_HOME}/atlases


# GUI for CLARITY input imgs

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	filepath=$(${MIRACL_HOME}/io/miracl_file_folder_gui.py -f file -s "$openstr")

    filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

#	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:o:l:m:v:" opt; do
    
	    case "${opt}" in

	        i)
            	inclar=${OPTARG}
            	;;

            o)
            	ort=${OPTARG}
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
		echo "ERROR: < -i => input down-sampled clarity nii> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "Down-sampled auto-fluorescence (or Thy1) channel (nii/nii.gz)" inclar

    printf "\n Input file path: ${inclar} \n"

	# check required input arguments

	if [ -z ${inclar} ];
	then
		usage
		echo "ERROR: <input clarity nii> was not chosen"
		exit 1
	fi


	# options gui 
	opts=$(${MIRACL_HOME}/io/miracl_io_gui_options.py -t "Reg options" -f "Orient code (def = ASL)" "Hemi [combined (def)/split]" "Labels resolution [vox] (def = 10 'um')" -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

	ort=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen orient code: $ort \n"

	hemi=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen hemi: $hemi \n"

	vox=`echo "${arr[2]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen vox (um): $vox \n"


fi


# get time

START=$(date +%s)


#---------------------------
#---------------------------



# 1) Process clarity Functions

# Function to check if file exists then runs other command

function ifdsntexistrun() 
{  

	local outfile="$1"; 
	local outstr="$2"; 
	local fun="${@:3}";  

	if [[ ! -f ${outfile} ]]; then

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
	
	ifdsntexistrun ${resclar} "Resmapling CLARITY input" ResampleImage 3 ${inclar} ${resclar} ${vox}x${vox}x${vox} ${ifspacing} ${interp}

	c3d ${resclar} -type short -o ${resclar}

}


# N4 bias correct

function biasfieldcorr()
{
	
	local resclar=$1
	local biasclar=$2	

	ifdsntexistrun ${biasclar} "Bias-correcting CLARITY image with N4" N4BiasFieldCorrection -d 3 -i ${resclar} -s 2 -o ${biasclar}

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

	ifdsntexistrun ${thrclar} "Thresholding CLARITY image" c3d ${biasclar} -threshold ${p1}% ${p2}% ${t1} ${t2} -o ${thrclar}

}


# Ero

function erode()
{
	
	local thrclar=$1
	local erorad=$2
	local eromask=$3	

	ifdsntexistrun ${eromask} "Eroding CLARITY mask" ImageMath 3 ${eromask} ME ${thrclar} ${erorad}

}


# Dil

function dilate()
{
	
	local eromask=$1
	local dilrad=$2
	local dilmask=$3

	ifdsntexistrun ${dilmask} "Dilating CLARITY mask" ImageMath 3 ${dilmask} MD ${eromask} ${dilrad}

}


# mask

function maskimage()
{
		
	local biasclar=$1
	local dilmask=$2
	local betclar=$3
		
	ifdsntexistrun ${betclar} "Removing CLARITY image outline artifacts" MultiplyImages 3 ${biasclar} ${dilmask} ${betclar}

	c3d ${betclar} -type short -o ${betclar}

}


# Orient 

function orientimg()
{

	local betclar=$1
	local orttag=$2
	local ortint=$3
	local orttype=$4
	local ortclar=$5

	ifdsntexistrun ${ortclar} "Orienting CLARITY to standard orientation" \
	c3d ${betclar} -orient ${orttag} -interpolation ${ortint} -type ${orttype} -o ${ortclar}

}


# Smooth image

function smoothimg()
{
	
	local ortclar=$1
	local sigma=$2
	local smclar=$3

	ifdsntexistrun ${smclar} "Smoothing CLARITY image" SmoothImage 3 ${ortclar} ${sigma} ${smclar} 1 1

	c3d ${smclar} -type short -o ${smclar}

}


# Crop to smallest roi

function croptosmall()
{
	
	local smclar=$1
	local trim=$2
	local clarroi=$3

	ifdsntexistrun ${clarroi} "Cropping CLARITY image to smallest ROI" c3d ${smclar} -trim ${trim}vox -type short -o ${clarroi}

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
	ifdsntexistrun ${initform} "Initializing registration ..." \
	 antsAffineInitializer 3 ${clarroi} ${allenref} ${initform} ${deg} ${radfrac} ${useprincax} ${localiter} &

    # kill after 3 min (gcc issue)
    pid=`echo $!`

    sleep 180

    kill ${pid}

	# Warp Allen
	ifdsntexistrun ${initallen} "initializing Allen template" antsApplyTransforms -i ${allenref} -r ${clarroi} -t ${initform} -o ${initallen}


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

    # convert init allen into int
    c3d ${initallen} -type int -o ${initallen}

	# Perform ANTs registration between CLARITY and Allen atlas

	ifdsntexistrun ${antsallen} "Registering CLARITY data to allen atlas ... this will take a while" \
	antsRegistrationMIRACL.sh -d 3 -f ${clarroi} -m ${initallen} -o ${regdir}/allen_clar_ants -t ${trans} -p ${prec} -n ${thrds} -s ${spldist} -r ${rad} | tee ${regdir}/ants_reg.log


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
    local inclar=${13}
    local reslbls=${14}
    local restif=${15}

    # Blank
#    local blank=$16
#    local blankres=${17}

    # Vox
    local vox=${16}

    # Res clar
    local smclarres=${17}

#     # Create empty image as ref
#    ifdsntexistrun ${blank} "Creating reference image" CreateImage 3 ${swplbls} ${blank} 0
#
#    ifdsntexistrun ${blankres} "Usampling reference image" ResampleImage 3 ${blank} ${blankres} ${vres}x${vres}x${vres} 0 1

    # Upsample ref
    vres=`python -c "print ${vox}/1000.0"`

    # res clar in
    ifdsntexistrun ${smclarres} "Usampling reference image" ResampleImage 3 ${smclar} ${smclarres} ${vres}x${vres}x${vres} 0 1

	# warp to registered clarity
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${smclarres} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff} ${initform} -o ${wrplbls}

	# orient to org 
	ifdsntexistrun ${ortlbls} "Orienting Allen labels" orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}

	# swap dim (x=>y / y=>x)
	ifdsntexistrun ${swplbls} "Swapping label dimensions" PermuteFlipImageOrientationAxes  3 ${ortlbls} ${swplbls}  1 0 2  0 0 0

	# create tif lbls
	ifdsntexistrun ${tiflbls} "Converting lbls to tif" c3d ${swplbls} -type ${orttypelbls} -o ${tiflbls}

	# upsample to img dimensions
    df=`echo ${inclar} | egrep -o "[0-9]{2}x_down" | egrep -o "[0-9]{2}"`

     # get img dim
    alldim=`PrintHeader ${inclar} 2`
    x=${alldim%%x*} ;
    yz=${alldim#*x} ; y=${yz%x*} ;
    z=${alldim##*x} ;

#    swpdim=`PrintHeader ${swplbls} 2`
#    sx=${swpdim%%x*} ;
#    syz=${swpdim#*x} ; sy=${syz%x*} ;

    ox=$(($y*$df)) ;
    oy=$(($x*$df)) ;

#	ifdsntexistrun ${reslbls} "Upsampling labels to CLARITY resolution" \
#	ResampleImage 3 ${swplbls} ${reslbls} ${ox}x${oy}x${oz} 1 1
#	c3d ${swplbls} -resample ${df}00x${df}00x${df}00% -interpolation ${ortintlbls} -type ${orttypelbls} -o ${reslbls}
	 # Can also resample with cubic (assuming 'fuzzy' lbls) or smooth resampled labels (c3d split) ... but > 700 lbls

    # create hres tif lbls
	ifdsntexistrun ${restif} "Converting high res lbls to tif" c3d ${swplbls} -resample ${ox}x${oy}x${z}mm -interpolation ${ortintlbls} -type ${orttypelbls} -o ${restif}


}

#---------------------------

# 4a) Warp input CLARITY to Allen Function

function warpinclarallen()
{

	# Ort clar
	inclar=$1
	ortclartag=$2
	ortclarint=$3
	ortclartype=$4
	orthresclar=$5

	# Reg to allen
	allenhres=$6
	initform=$7
	antsaff=$8
	antsinvwarp=$9

	regorgclar=${10}

	# Orient channel to std
	orientimg ${inclar} ${ortclartag} ${ortclarint} ${ortclartype} ${orthresclar}

	# Apply warps
	ifdsntexistrun ${regorgclar} "Applying ants deformation to input CLARITY" \
	antsApplyTransforms -r ${allenhres} -i ${orthresclar} -n Bspline -t [ ${initform}, 1 ] [ ${antsaff}, 1 ] ${antsinvwarp} -o ${regorgclar} --float

}

#---------------------------

# 4b) Warp down 3x CLARITY (high res) to Allen Function


function warphresclarallen()
{

	# Ort clar
	hresclar=$1
	ortclartag=$2
	ortclarint=$3
	ortclartype=$4
	orthresclar=$5

	# Reg to allen
	allenhres=$6
	initform=$7
	antsaff=$8
	antsinvwarp=$9
	
	regorgclar=${10}

	# Orient channel to std
	orientimg ${hresclar} ${ortclartag} ${ortclarint} ${ortclartype} ${orthresclar}

	# Apply warps
	ifdsntexistrun ${regorgclar} "Applying ants deformation to high-res CLARITY" \
	antsApplyTransforms -r ${allenhres} -i ${orthresclar} -n Bspline -t [ ${initform}, 1 ] [ ${antsaff}, 1 ] ${antsinvwarp} -o ${regorgclar} --float

}


#---------------------------
#---------------------------



# Build main function

function main()
{

# 1) Process clarity


	# resample to 0.05mm voxel
	resclar=${regdir}/clar_res0.05.nii.gz
	resampleclar ${inclar} 0.05 0 4 ${resclar}

	# N4 bias correct
	biasclar=${regdir}/clar_res0.05_bias.nii.gz
	biasfieldcorr ${resclar} ${biasclar}

	# Remove outline w erosion & dilation

	# Thr
	thrclar=${regdir}/clar_res0.05_bias_thr.nii.gz
	thresh ${biasclar} 2 50 0 1 ${thrclar}

	# Ero (remove any components attached to the brain)
	eromask=${regdir}/clar_res0.05_ero_mask.nii.gz
	erode ${thrclar} 3 ${eromask}

    # Get largest component
    conncomp=${regdir}/clar_res0.05_ero_mask_comp.nii.gz
    c3d ${eromask} -comp -threshold 1 1 1 0 -o ${conncomp}

	# Dil
	dilmask=${regdir}/clar_res0.05_dil_mask.nii.gz
	dilate ${conncomp} 3 ${dilmask}

	# Mask
	betclar=${regdir}/clar_res0.05_bias_bet.nii.gz
	maskimage ${biasclar} ${dilmask} ${betclar}

	# Orient
	ortclar=${regdir}/clar_res0.05_ort.nii.gz

	if [[ -z ${ort} ]]; then
	    ort=ARS
	fi
    ## if A-P flipped (PLS) & if R-L -> ALS

	orientimg ${betclar} ${ort} Cubic short ${ortclar}

	# Smooth
	smclar=${regdir}/clar_res0.05_sm.nii.gz
	smoothimg ${ortclar} 1 ${smclar}

	# Crop to smallest roi
#	clarroi=${regdir}/clar_res0.05_ort_sm_roi.nii.gz
#	croptosmall ${smclar} 5 ${clarroi}

	# make clarity copy
	clarlnk=${regdir}/clar.nii.gz
	if [[ ! -f ${clarlnk} ]]; then cp ${smclar} ${clarlnk} ; fi

	#---------------------------


# 2a) initialize registration

	# Allen atlas template
    allenref=${atlasdir}/ara/template/average_template_25um.nii.gz

	initform=${regdir}/init_tform.mat

	# Init parms

	deg=1 # search increment in degrees
	radfrac=1 # arc around principal axis
	useprincax=0 # rotation searched around principal axis
	localiter=500 # num of iteration for optimization at search point

	# Out Allen
	initallen=${regdir}/init_allen.nii.gz


	initclarallenreg ${clarlnk} ${allenref} ${initform} ${deg} ${radfrac} ${useprincax} ${localiter} ${initallen}


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
	antsallen=${regdir}/allen_clar_antsWarped.nii.gz


	regclarallen ${clarroi} ${initallen} ${trans} ${spldist} ${rad} ${prec} ${thrds} ${antsallen}


	#---------------------------


# 3) Warp Allen labels to original CLARITY (down sampled 2x)


	# Tforms
	antswarp=${regdir}/allen_clar_ants1Warp.nii.gz
	antsaff=${regdir}/allen_clar_ants0GenericAffine.mat

	# If want to warp multi-res / hemi lbls
	
	if [[ -z ${lbls} ]]; then

		if [[ -z ${hemi} ]]; then
			
			hemi=combined

		fi

		if [[ -z ${vox} ]]; then
			
			vox=10

		fi

        lbls=${atlasdir}/ara/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz

	fi

	base=`basename ${lbls}`
	lblsname=${base%%.*};

	# Out lbls
	wrplbls=${regdirfinal}/${lblsname}_clar_downsample.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
	swplbls=${regdir}/${lblsname}_ants_swp.nii.gz
	tiflbls=${regdirfinal}/${lblsname}_clar_vox.tif
	reslbls=${regdirfinal}/${lblsname}_clar.nii.gz
	restif=${regdirfinal}/${lblsname}_clar.tif

	smclarres=${regdirfinal}/clar_downsample_res${vox}um.nii.gz

	# upsample in python now
	# warpallenlbls $smclar $lbls $antswarp $antsaff $initform $wrplbls LPI NearestNeighbor short $ortlbls $resclar $reslbls

    # setting lbl ort
    o=${ort:0:1}
    r=${ort:1:1}
    t=${ort:2:2}

    ol=${r}

    if [ ${o} == "A" ]; then
        rl="P"
    elif [ ${o} == "P" ]; then
        rl="A"
    elif [ ${o} == "R" ]; then
        rl="L"
    elif [ ${o} == "L" ]; then
        rl="R"
    elif [ ${o} == "S" ]; then
        rl="I"
    elif [ ${o} == "I" ]; then
        rl="S"
    fi

    if [ ${t} == "A" ]; then
        tl="P"
    elif [ ${t} == "P" ]; then
        tl="A"
    elif [ ${t} == "R" ]; then
        tl="L"
    elif [ ${t} == "L" ]; then
        tl="R"
    elif [ ${t} == "S" ]; then
        tl="I"
    elif [ ${t} == "I" ]; then
        tl="S"
    fi

    ortlbl="$ol$rl$tl"

	warpallenlbls ${smclar} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} ${ortlbl} NearestNeighbor short ${ortlbls} ${swplbls} ${tiflbls} ${inclar} ${reslbls} ${restif} ${vox} ${smclarres}


	#---------------------------


# 4) Warp input CLARITY to Allen


	# ort hres clar
#	orthresclar=${regdir}/hres_EYFP_ort.nii.gz
	ortinclar=${regdir}/clar_ort.nii.gz

	# hres Allen
	allenhres=${atlasdir}/ara/template/average_template_10um.nii.gz

	# ants inv warp
	antsinvwarp=${regdir}/allen_clar_ants1InverseWarp.nii.gz

	# out warp hres clar
#	regorgclar=${regdirfinal}/hresclar_allen_ants.nii.gz
    regorgclar=${regdirfinal}/clar_allen_space.nii.gz


    warpinclarallen ${inclar} ${ort} Cubic short ${ortinclar} ${allenhres} ${initform} ${antsaff} ${antsinvwarp} ${regorgclar}
#	warphresclarallen ${hresclar} ALS Cubic short ${orthresclar} $allenhres $initform $antsaff $antsinvwarp $regorgclar

}


#--------------------


# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Registration and Allen label warping done in $DIFF minutes. Have a good day!"


# TODOs
# TODOlp: add if already oriented
# TODOlp: add settings file to read for pars