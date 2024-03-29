#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version.txt`
	printf "\n MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{
    
    cat <<usage

	1) Registers in-vivo or ex-vivo MRI data to Allen Reference mouse brain Atlas
	2) Warps Allen annotations to the MRI space

	if no inputs are given function will run in GUI mode

	For command-line / scripting

	Usage: miracl reg mri_allen_ants -i [ input invivo or exvivo MRI nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -b [ olfactory bulb ] -s [ skull strip ] -n [ no orient needed ]

    Example: miracl reg mri_allen_ants -i inv_mri.nii.gz -o RSP -m combined -v 25

    arguments (required):
		i.  input MRI nii
            Preferably T2-weighted

    optional arguments:
        o.  orient code (default: RSP)
            to orient nifti from original orientation to "standard/Allen" orientation
        m.  hemisphere mirror (default: combined)
            warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
			accepted inputs are: <split> or <combined>
        v.  labels voxel size/Resolution in um (default: 10)
			accepted inputs are: 10, 25 or 50
        l.  input Allen labels to warp (default: annotation_hemi_combined_10um.nii.gz )
			input labels could be at a different depth than default labels
			If l. is specified (m & v cannot be specified)
        b.  olfactory bulb included in brain, binary option (default: 0 -> not included)
        s.  skull strip or not, binary option (default: 1 -> skull-strip)
        f.  FSL skull striping fractional intensity (default: 0.3), smaller values give larger brain outlines
        n.  No orientation needed (input image in "standard" orientation), binary option (default: 0 -> orient)

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
echo "${MIRACL_HOME}"

fslcmd=`which fsl`

if [ -z "${fslcmd// }" ];
then
	echo "ERROR: < FSL not initialized .. please intall it & run init/check_depend.sh > not specified"
	exit 1
fi

# ANTs
ANTS=`which antsRegistration`
if [[ -z ${ANTS} ]];
  then
    echo "ANTS program can't be found. Please (re)define \$ANTSPATH in your environment."
    exit 1
else
	printf "\n ANTS path check: OK... \n"
fi

# C3D
c3dpath=`which c3d`
if [ -z ${c3dpath} ]; then
    printf "\n ERROR: c3d not initialized. Please setup miracl & rerun script \n"
	exit 1
else
	printf "\n c3d path check: OK... \n"
fi

# ants_miracl_mr is required. Make sure a symbolic link is added
ants_miracl_mr_path=`which ants_miracl_mr`
if [[ ! -z "${ants_miracl_mr_path}" ]]; then
	if [[ -f "${MIRACL_HOME}/../depends/ants/antsRegistrationMIRACL_MRI.sh" ]]; then
		ln -s "${MIRACL_HOME}/../depends/ants/antsRegistrationMIRACL_MRI.sh" /usr/bin/ants_miracl_mr && \
		chmod +x /usr/bin/ants_miracl_mr
	else
		echo "\n ERROR: ants_miracl_mr is not initialized. Please ensure that antsRegistrationMIRACL_MRI.sh has been downloaded to the necessary directory and rerun the script"
		exit 1
	fi
fi

#----------

# Init atlas dir

atlasdir=$( dirname ${MIRACL_HOME} )/atlases


# GUI for MRI input imgs

function choose_file_gui()
{
	local openstr=$1
	local ftype=$2
	local _inpath=$3

    filepath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f file -s "$openstr" -t "$ftype")

	filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

#	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:o:l:m:v:b:s:f:n:" opt; do
    
	    case "${opt}" in

	        i)
            	inmr=${OPTARG}
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

            b)
            	bulb=${OPTARG}
            	;;

            s)
            	skull=${OPTARG}
            	;;

            f)
            	frac=${OPTARG}
            	;;

            n)
            	noort=${OPTARG}
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

	#choose_file_gui "In-vivo or Ex-vivo MRI" "*.nii *.nii.gz" inmr

	# options gui
	opts=$(${MIRACL_HOME}/conv/miracl_conv_gui_options.py -t "Reg options" -v "In-vivo or Ex-vivo MRI" \
	-f "Orient code (def = RSP)" "Labels Hemi [combined (def)/split]" "Labels resolution [vox] (def = 10 'um')"  \
	 "olfactory bulb incl. (def = 0)" "skull strip (def = 1)" "No orient (def = 0)"  -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

    inmr=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    # check required input arguments

	if [[ -z ${inmr} ]] || [[ "${inmr}" == "No file was chosen" ]];
	then
		usage
		echo "ERROR: <input MRI nii> was not chosen"
		exit 1
	fi

    printf "\n Input file path: ${inmr} \n"


	ort=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen orient code: $ort \n"

	hemi=`echo "${arr[2]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen labels hemi option: $hemi \n"

	vox=`echo "${arr[3]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen vox (um): $vox \n"

	bulb=`echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen olfactory bulb option: $bulb \n"

    skull=`echo "${arr[5]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen skull strip option: $skull \n"

    noort=`echo "${arr[6]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen No orientation option: $noort \n"

fi



# make reg dir

regdirfinal=$PWD/reg_final
regdir=$PWD/mr_allen_reg


if [[ ! -d ${regdir} ]]; then

    printf "\n Creating registration folder\n"
    mkdir -p ${regdirfinal} ${regdir}

fi

# output log file of script

exec > >(tee -i ${regdir}/mri_allen_script.log)
exec 2>&1


#---------------------------

# set defaults and assert (check for input errors)


# orient code
if [[ -z ${ort} ]]; then
    ort=RSP
fi

# If want to warp multi-res / hemi lbls

if [[ -z ${lbls} ]]; then

    if [[ -z ${hemi} ]]; then

        hemi=combined

    else

        if [ "${hemi}" != "combined" ] && [ "${hemi}" != "split" ]; then

            printf "ERROR: < -m => (hemi) > only takes as inputs: combined or split"
            exit 1
        fi

    fi

    if [[ -z ${vox} ]]; then

        vox=10

    else

        if [ "${vox}" != 10 ] && [ "${vox}" != 25 ] && [ "${vox}" != 50 ] ; then

            printf "ERROR: < -v => (vox) > only takes as inputs: 10, 25 or 50"
            exit 1
        fi

    fi

    lbls=${atlasdir}/ara/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz

fi

# no orient
if [[ -z ${noort} ]]; then
    noort=0
else

    if [ "${noort}" != 0 ] && [ "${noort}" != 1 ]; then

    printf "ERROR: < -n = > (noort) > only takes as inputs: 0 or 1"
    exit 1

    fi
fi

# skull strip
if [[ -z ${skull} ]]; then
    skull=1
else

    if [ "${skull}" != 0 ] && [ "${skull}" != 1 ]; then

    printf "ERROR: < -s = > (skull) > only takes as inputs: 0 or 1"
    exit 1

    fi

fi

# olfactory bulb
if [[ -z ${bulb} ]] ; then
    bulb=0
else

    if [ "${bulb}" != 0 ] && [ "${bulb}" != 1 ]; then

    printf "ERROR: < -b = > (bulb) > only takes as inputs: 0 or 1"
    exit 1

    fi
fi

# fractional intensity for skull-strip
if [[ -z ${frac} ]] ; then
    frac=0.3
fi

# get time

START=$(date +%s)


#---------------------------
#---------------------------



# 1) Process MRI Functions

# Function to check if file exists then runs other command

function ifdsntexistrun() 
{  

	local outfile="$1"; 
	local outstr="$2"; 
	local fun="${@:3}";  

	if [[ ! -f ${outfile} ]]; then

		printf "\n $outstr \n"; 
		echo "$fun"; 
		eval "${fun}";

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
    ifdsntexistrun ${thrmr} "Thresholding MRI image" fslmaths ${biasmr} -thrP ${thr} ${thrmr}

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


# change header * 10 dims

function mulheader()
{

	local unhdmr=$1
	local mulfac=$2
	local hdmr=$3

	# split each pixdim value into an array to extract the last value
	dim1_arr=( $(fslinfo ${unhdmr} | grep pixdim1 | tr " " "\t" ) )
	x="${dim1_arr[1]}"

	dim2_arr=( $(fslinfo ${unhdmr} | grep pixdim2 | tr " " "\t" ) )
	y="${dim2_arr[1]}"

	dim3_arr=( $(fslinfo ${unhdmr} | grep pixdim3 | tr " " "\t" ) )
	z="${dim3_arr[1]}"

    nx=`echo ${x}*${mulfac} | bc` ;
    ny=`echo ${y}*${mulfac} | bc` ;
    nz=`echo ${z}*${mulfac} | bc` ;

    ifdsntexistrun ${hdmr} "Altering MRI header" c3d ${unhdmr} -spacing ${nx}x${ny}x${nz}mm -o ${hdmr}

}

# skull strip

function skullstrip()
{

	local skullmr=$1
	local betmr=$2
	local frac=$3

    com=`fslstats ${skullmr} -C`

#    ifdsntexistrun ${betmr} "Skull stripping MRI image" bet ${skullmr} ${betmr} -r 55 -c ${com} -f ${frac}
    ifdsntexistrun ${betmr} "Skull stripping MRI image" bet ${skullmr} ${betmr} -c ${com} -f ${frac} -R

}


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


# Smooth image

function smoothimg()
{

	local ortmr=$1
	local sigma=$2
	local smmr=$3

	ifdsntexistrun $smmr "Smoothing MRI image" SmoothImage 3 $ortmr ${sigma} $smmr 0 1
#    ifdsntexistrun ${smmr} "Smoothing MRI image" c3d ${ortmr} -smooth ${sigma}x${sigma}x${sigma}mm -o ${smmr}

}

#---------------------------

# 2a) initialize registration Function

function initmrallenreg()
{

	# Init imgs
	mrlnk=$1
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
	 antsAffineInitializer 3 ${mrlnk} ${allenref} ${initform} ${deg} ${radfrac} ${useprincax} ${localiter}


	# Warp Allen
	ifdsntexistrun ${initallen} "initializing Allen template" antsApplyTransforms -i ${allenref} -r ${mrlnk} -t ${initform} -o ${initallen}


}

#---------------------------

# 2b) Register to Allen atlas Function

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

	# Perform ANTs registration between MRI and Allen atlas

	ifdsntexistrun ${antsallen} "Registering MRI data to allen atlas ... this will take a while" \
	ants_miracl_mr -d 3 -f ${mrprereg} -m ${allen} -o ${regdir}/allen_mr_ants -t ${trans} -p ${prec} -n ${thrds} -s ${spldist} -r ${rad} | tee ${regdir}/ants_reg.log


}


#---------------------------


# 3) Warp Allen labels to original MRI Function


function warpallenlbls()
{

	# In imgs
	local mrlnk=$1
	local lbls=$2

	# In tforms
	local antswarp=$3
	local antsaff=$4
#	local initform=$5

	# Out lbls
	local wrplbls=$5

	# warp to registered MRI
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	antsApplyTransforms -d 3 -r ${mrlnk} -i ${lbls} -n MultiLabel -t ${antswarp} ${antsaff} -o ${wrplbls} --float


}

#---------------------------

# 4) Warp MRI to Allen space Function

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
	antsApplyTransforms -r ${allenhres} -i ${orthresmr} -n Bspline -t [ ${initform}, 1 ] [ ${antsaff}, 1 ] ${antsinvwarp} -o ${regorgmr} --float

}


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

	# Orient
	ortmr=${regdir}/mr_bias_thr_ort.nii.gz

    if [[ "${noort}" == 0 ]]; then

	    orientimg ${thrmr} ${ort} Cubic short ${ortmr}

    else

        ortmr=${thrmr}

    fi

    # Crop to smallest roi
	mrroi=${regdir}/mr_bias_thr_roi.nii.gz
	croptosmall ${ortmr} ${mrroi}


    if [[ "${skull}" == 1 ]]; then

        # Change header * 10 dims
        hdmr=${regdir}/mr_bias_thr_ort_hd.nii.gz
        mulheader ${mrroi} 10 ${hdmr}

        # Skull strip
        betmr=${regdir}/mr_bias_thr_ort_bet.nii.gz
        skullstrip ${hdmr} ${betmr} ${frac}

        # Update back header
        orghdmr=${regdir}/mr_bias_thr_ort_bet_orghd.nii.gz
        mulheader ${betmr} "0.1" ${orghdmr}

    else

        orghdmr=${mrroi}

    fi

    # Smooth
    smmr=${regdir}/mr_bias_thr_ort_bet_sm.nii.gz
    smoothimg ${orghdmr} 1 ${smmr}
#    smoothimg ${orghdmr} 0.25 ${smmr}

	# make MRI copy
	mrlnk=${regdir}/mr.nii.gz
	if [[ ! -f ${mrlnk} ]]; then cp ${smmr} ${mrlnk} ; fi

	#---------------------------

# 2a) initialize registration

    # Allen atlas template

    if [[ "${bulb}" == 0 ]]; then
        allenref=${atlasdir}/ara/template/average_template_50um_OBmasked.nii.gz

    elif [[ "${bulb}" == 1 ]]; then
        allenref=${atlasdir}/ara/template/average_template_50um.nii.gz
    fi

#	initform=${regdir}/init_tform.mat
#
#	# Init parms
#
#	deg=2 # search increment in degrees
#	radfrac=0.05 # arc around principal axis
#	useprincax=0 # rotation searched around principal axis
#	localiter=100 # num of iteration for optimization at search point
#
#	# Out Allen
#	initallen=${regdir}/init_allen.nii.gz
#
#	initmrallenreg ${mrlnk} ${allenref} ${initform} ${deg} ${radfrac} ${useprincax} ${localiter} ${initallen}
#

	#---------------------------

# 2b) Register to Allen atlas
	

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

	# Out Allen
	antsallen=${regdir}/allen_mr_antsWarped.nii.gz

#	regmrallen ${orghdmr} ${initallen} ${trans} ${spldist} ${rad} ${prec} ${thrds} ${antsallen}
    regmrallen ${mrlnk} ${allenref} ${trans} ${spldist} ${rad} ${prec} ${thrds} ${antsallen}

	#---------------------------


# 3) Warp Allen labels to MRI

	# Tforms
	antswarp=${regdir}/allen_mr_ants1Warp.nii.gz
	antsaff=${regdir}/allen_mr_ants0GenericAffine.mat

    base=`basename ${lbls}`
	lblsname=${base%%.*};

    # Out lbls
	wrplbls=${regdirfinal}/${lblsname}_ants.nii.gz

#	warpallenlbls ${mrlnk} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls}
    warpallenlbls ${mrlnk} ${lbls} ${antswarp} ${antsaff} ${wrplbls}

	#---------------------------

# 4) Warp input MRI to Allen

#	# ort hres mr
#	ortinmr=${regdir}/org_mr_ort.nii.gz
#
#	# hres Allen
#	allenhres=${atlasdir}/ara/template/average_template_10um.nii.gz
#
#	# ants inv warp
#	antsinvwarp=${regdir}/allen_mr_ants1InverseWarp.nii.gz
#
	# out warp hres mr
    regmrallen=${regdirfinal}/mr_allen_ants.nii.gz
    antsinvmr=${regdir}/allen_mr_antsInverseWarped.nii.gz
#
#    warpinmrallen ${inmr} RSP Cubic short ${ortinmr} ${allenhres} ${initform} ${antsaff} ${antsinvwarp} ${regorgmr}

    if [[ ! -f ${regmrallen} ]]; then cp ${antsinvmr} ${regmrallen} ; fi

}

#--------------------


# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

miracl utils end_state -f "Registration and Allen labels warping" -t "$DIFF minutes"


#--------------------
# TODOs

# TODOlp: add stroke mask later

# create output file for successful completion
command="${vox}\n${ort}"
echo -e $command >> "reg_command.log"