#!/usr/bin/env bash

# get version
function getversion()
{
	ver=`cat ${MIRACL_HOME}/version.txt`
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

	Usage: `basename $0` -i [ input clarity nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -s [ side if hemisphere ony ] -b [ olfactory buld included ]

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

        s.  side, if only registering a hemisphere instead of whole brain
            accepted inputs are: rh (right hemisphere) or lh (left)

        f.  save mosaic figure (.png) of allen labels registered to clarity (default: 1)

        b.  olfactory bulb included in brain, binary option (default: 0 -> not included)

        p.  if utilfn intensity correction already run, skip correction inside registration (default: 0)

        w.  warp high-res clarity to Allen space (default: 0)

	----------

	Main Outputs

        reg_final/clar_allen_space.nii.gz: Clarity data in Allen reference space

        reg_final/clar_downsample_res(vox)um.nii.gz : Clarity data downsampled and oriented to "standard"

        reg_final/annotation_hemi_(hemi)_(vox)um_clar_downsample.nii.gz : Allen labels registered to downsampled Clarity

        reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif : Allen labels registered to oriented Clarity

        reg_final/annotation_hemi_(hemi)_(vox)um_clar.tif : Allen labels registered to original (full-resolution) Clarity


        - To visualize Allen labels in downsampled clarity data space (from command line):

            itksnap -g reg_final/clar_downsample_res(vox)um.nii.gz -s reg_final/annotation_hemi_(hemi)_(vox)um_clar_downsample.nii.gz -l \$snaplut


        - To visualize clarity data in Allen space - assuming chosen v/vox 10um
            from command line:

                itksnap -g \$allen10 -o reg_final/clar_allen_space.nii.gz -s \$lbls10 -l \$snaplut

            from GUI:

                \$allen10 = \$MIRACL_HOME/atlases/ara/template/average_template_10um.nii.gz -> (Main Image)

                \$lbls10 = \$MIRACL_HOME/atlases/ara/annotation/annotation_hemi_combined_10um.nii.gz -> (Segmentation)

                \$snaplut = \$MIRACL_HOME/atlases/ara/ara_snaplabels_lut.txt -> (Label Descriptions)


        - Full resolution Allen labels in original clarity space (.tif) can be visualized by Fiji


    ----------

	Dependencies:

		- ANTs
		https://github.com/stnava/ANTs			
		
		- c3d
		https://sourceforge.net/projects/c3d

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2017
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
	local ftype=$2
	local _inpath=$3

	filepath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f file -s "$openstr" -t "$ftype")

    filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	eval ${_inpath}="'$filepath'"

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:o:l:m:v:s:b:f:p:w:" opt; do
    
	    case "${opt}" in

	        i)
            	inclar="${OPTARG}"
            	;;

            o)
            	ort="${OPTARG}"
            	;;

        	l)
            	lbls="${OPTARG}"
            	;;

        	m)
            	hemi="${OPTARG}"
            	;;

        	v)
            	vox="${OPTARG}"
            	;;

            s)
            	side="${OPTARG}"
            	;;

            b)
            	bulb="${OPTARG}"
            	;;

            f)
            	savefig="${OPTARG}"
            	;;

            p)
                prebias="${OPTARG}"
                ;;

            w)
                warphres="${OPTARG}"
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

	#choose_file_gui "Down-sampled auto-fluorescence (or Thy1) channel" "*.nii *.nii.gz" inclar

	# options gui 
	opts=$(${MIRACL_HOME}/conv/miracl_conv_gui_options.py -t "Reg options" -v "Down-sampled auto-fluorescence (or Thy1) channel "  \
	-f "Orient code (def = ASL)" "Labels Hemi [combined (def)/split]" "Labels resolution [vox] (def = 10 'um')"  \
	  "olfactory bulb incl. (def = 0)" "side (def = None)" "extra int correct (def = 0)" -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

    inclar=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Input file path: ${inclar} \n"

	# check required input arguments

	if [[ -z ${inclar} ]] || [[ "${inclar}" == "No file was chosen" ]];
	then
		usage
		echo "ERROR: <input clarity nii> was not chosen"
		exit 1
	fi

	ort=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen orient code: $ort \n"

	hemi=`echo "${arr[2]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen labels hemi option: $hemi \n"

	vox=`echo "${arr[3]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen vox (um): $vox \n"

	bulb=`echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen olfactory bulb option: $bulb \n"

	side=`echo "${arr[5]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen side option: $side \n"

    field=`echo "${arr[6]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen extra intensity correct: $field \n"


fi


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


#---------------------------


# set defaults and assert (check for input errors)

# orient code
if [[ -z ${ort} ]]; then
    ort=ARS
fi
## if A-P flipped (PLS) & if R-L -> ALS

# If want to warp multi-res / hemi lbls
if [[ -z ${lbls} ]]; then

    if [[ -z ${hemi} ]]; then

        hemi=combined

    else

        if [[ "${hemi}" != "combined" ]] && [[ "${hemi}" != "split" ]]; then

            printf "ERROR: < -m => (hemi) > only takes as inputs: combined or split"
            exit 1
        fi

    fi

    if [[ -z ${vox} ]]; then

        vox=10

    else

        if [[ "${vox}" != 10 ]] && [[ "${vox}" != 25 ]] && [[ "${vox}" != 50 ]] ; then

            printf "ERROR: < -v => (vox) > only takes as inputs: 10, 25 or 50"
            exit 1
        fi

    fi

    lbls=${atlasdir}/ara/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz

fi

# set side for hemisphere registration
if [[ -z ${side} ]] ; then
    side=""
elif [[ "${side}" == "rh" ]]; then
    side="_right"
elif [[ "${side}" == "lh" ]]; then
    side="_left"
else
    printf "ERROR: < -s => (side) > only takes as inputs: rh or lh"
    exit 1
fi

# olfactory bulb
if [[ -z ${bulb} ]] ; then
    bulb=0
else

    if [[ "${bulb}" != 0 ]] && [[ "${bulb}" != 1 ]]; then

    printf "ERROR: < -b = > (bulb) > only takes as inputs: 0 or 1"
    exit 1

    fi

fi

# pre-bias
if [[ -z ${prebias} ]] ; then
    prebias=0
fi

# save mosaic
if [[ -z ${savefig} ]] ; then
    savefig=1
fi

# warp high-res clar
if [[ -z ${warphres} ]] ; then
    warphres=0
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
		eval "${fun}";

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
	
	ifdsntexistrun ${resclar} "Resmapling CLARITY input" \
	ResampleImage 3 ${inclar} ${resclar} ${vox}x${vox}x${vox} ${ifspacing} ${interp}

	c3d ${resclar} -type ushort -o ${resclar}

}

# get brain mask (thresh & conn comp)

function getbrainmask()
{
    local resclar=$1
    local sharp=$2
    local median=$3
    local brain=$4
    local mask=$5
    local biasin=$6
    local otsumaskthr=$7
    local otsumask=$8
    local otsucp=$9
    local otsu=${10}

    # sharpen
    ifdsntexistrun ${sharp} "Sharpening image" ImageMath 3 ${sharp} Sharpen ${resclar}

    # smooth
    ifdsntexistrun ${median} "Median Filtering" SmoothImage 3 ${sharp} 2 ${median} 1 1

    # bias correct in
    ifdsntexistrun ${biasin} "Bias correcting input" N3BiasFieldCorrection 3 ${median} ${biasin} 2
#    ifdsntexistrun ${biasin} "Bias correcting input" N4BiasFieldCorrection -i ${median} -o ${biasin} -s 2

    # Otsu threshold
    ifdsntexistrun ${otsumaskthr} "Otsu thresholding" ThresholdImage 3 ${biasin} ${otsumaskthr} Otsu 6

    # create mask
#    ifdsntexistrun ${otsumask} "Thresholding mask" ThresholdImage 3 ${otsumaskthr} ${otsumask} 3 6
    ifdsntexistrun ${otsumask} "Thresholding mask" ThresholdImage 3 ${otsumaskthr} ${otsumask} 2 6

    # get masked
#    ifdsntexistrun ${otsucp} "Create masked image" MultiplyImages 3 ${biasin} ${otsumask} ${otsucp} 1
    ifdsntexistrun ${otsu} "Create masked image" MultiplyImages 3 ${biasin} ${otsumask} ${otsu} 1

#    ifdsntexistrun ${otsu} "Copying transform" c3d ${median} ${otsucp} -copy-transform -o ${otsu}

    # center of gravity
    cog=`fslstats ${otsu} -C`

    # bet
    ifdsntexistrun ${mask} "Skull stripping" bet ${otsu} ${brain} -c ${cog} -R -r 25000 -m

    c3d ${median} ${brain} -copy-transform -o ${brain}


}
# N4 bias correct

function biasfieldcorr()
{
	
	local resclar=$1
	local biasclar=$2
	local mask=$3

    # make sure same clar & mask occupy same space
    c3d ${resclar} ${mask} -copy-transform -o ${mask}

	ifdsntexistrun ${biasclar} "Bias-correcting CLARITY image with N4" \
	N4BiasFieldCorrection -d 3 -i ${resclar} -s 2 -t [0.15,0.01,200] -x ${mask} -o ${biasclar}

}

# Extra field correct

function extrabiasfieldcorr()
{

	local biasclar=$1
	local mask=$2

    printf"\n Performing extra bias correction step\n"
    c3d ${biasclar} -as B -thresh 65% 75% 1 0 ${mask} -times -push B -times -scale 5 -push B -add -o ${biasclar}


}

# Pad image

function padimage()
{

    local biasclar=$1
    local padclar=$2

    ifdsntexistrun ${padclar} "Padding image with 15% of voxels" c3d ${biasclar} -pad 15% 15% 0 -o ${padclar}

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

	ifdsntexistrun ${thrclar} "Thresholding CLARITY image" \
	c3d ${biasclar} -threshold ${p1}% ${p2}% ${t1} ${t2} -o ${thrclar}

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
		
	ifdsntexistrun ${betclar} "Removing CLARITY image outline artifacts" \
	MultiplyImages 3 ${biasclar} ${dilmask} ${betclar}

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

#	ifdsntexistrun ${smclar} "Smoothing CLARITY image" SmoothImage 3 ${ortclar} ${sigma} ${smclar} 1 1
    ifdsntexistrun ${smclar} "Smoothing CLARITY image" c3d ${ortclar} -smooth ${sigma}vox -o ${smclar}


}


# Crop to smallest roi

function croptosmall()
{
	
	local smclar=$1
	local trim=$2
	local clarroi=$3

	ifdsntexistrun ${clarroi} "Cropping CLARITY image to smallest ROI" \
	c3d ${smclar} -trim ${trim}vox -type ushort -o ${clarroi}

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
	 antsAffineInitializer 3 ${clarroi} ${allenref} ${initform} ${deg} ${radfrac} ${useprincax} ${localiter} 2> /dev/null &

    # kill after 3 min (gcc issue)
    if [[ ! -f "${initallen}" ]] ; then
        sleep 180

        kill -9 $(ps -e | grep antsAffineInit | awk '{print $1}')
    fi

	# Warp Allen
	ifdsntexistrun ${initallen} "initializing Allen template" \
	 antsApplyTransforms -i ${allenref} -r ${clarroi} -t ${initform} -o ${initallen}


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
	ants_miracl_clar -d 3 -f ${clarroi} -m ${initallen} -o ${regdir}/allen_clar_ants -t ${trans} -p ${prec} \
	 -n ${thrds} -s ${spldist} -r ${rad} | tee ${regdir}/ants_reg.log


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
	local ortlbls=$7

	# swap lbls
	local swplbls=$8
	local tiflbls=$9
	
	# Up lbls
    local inclar=${10}
    local reslbls=${11}
    local restif=${12}

    # Vox
    local vox=${13}

    # Res clar
    local smclarres=${14}

    # lbls to org nii
    local inclar=${15}
    local orgortlbls=${16}
    local lblsorgnii=${17}

    local wrplblsorg=${18}
    local unpadtif=${19}

    # Upsample ref
    vres=`python -c "print (${vox}/1000.0)"`

    # res clar in
    ifdsntexistrun ${smclarres} "Usampling reference image" \
     ResampleImage 3 ${smclar} ${smclarres} ${vres}x${vres}x${vres} 0 0

    # convert to ushort
    ConvertImagePixelType ${smclarres} ${smclarres} 3

	# warp to registered clarity
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
    antsApplyTransforms -d 3 -r ${smclarres} -i ${lbls} -n MultiLabel -t ${antswarp} ${antsaff} ${initform} \
    -o ${wrplbls} --float

    # get org tag
	ortmatrix=`PrintHeader ${inclar} 4 | tr 'x' ' '`

	ifdsntexistrun ${ortlbls} "Orienting Allen labels" SetDirectionByMatrix ${wrplbls} ${ortlbls} ${ortmatrix}

	# swap dim (x=>y / y=>x)
	ifdsntexistrun ${swplbls} "Swapping label dimensions" \
	 PermuteFlipImageOrientationAxes 3 ${ortlbls} ${swplbls}  1 0 2  0 0 0

	ifdsntexistrun ${unpadtif} "Converting lbls to tif" \
	 PermuteFlipImageOrientationAxes 3 ${ortlbls} ${unpadtif}  1 0 2  0 0 0

    ifdsntexistrun ${tiflbls} "Un-padding high res tif" c3d ${unpadtif} -pad -10% -10% -o ${tiflbls}

	# upsample to img dimensions
    df=`echo ${inclar} | egrep -o "[0-9]{2}x_down" | egrep -o "[0-9]{2}"`

    # get img dim
    alldim=`PrintHeader ${inclar} 2`
    x=${alldim%%x*} ;
    yz=${alldim#*x} ; y=${yz%x*} ;
    z=${alldim##*x} ;

    ox=$(($y*$df)) ;
    oy=$(($x*$df)) ;
    oz=$(($z*$df)) ;

    # create hres tif lbls
    ifdsntexistrun ${restif} "Converting high res lbls to tif" \
     c3d ${tiflbls} -resample ${ox}x${oy}x${oz}mm -o ${restif}

    # warp nifti to org space
    orgspacing=`PrintHeader ${inclar} 1`

    ifdsntexistrun ${wrplblsorg} "Resampling labels to original space" \
    ResampleImage 3 ${wrplbls} ${wrplblsorg} ${orgspacing} 0 1

    ifdsntexistrun ${orgortlbls} "Orienting Allen labels to original space" \
    SetDirectionByMatrix ${wrplblsorg} ${orgortlbls} ${ortmatrix}

    # extract region
    lblsdim=`PrintHeader ${orgortlbls} 2`
    lx=${lblsdim%%x*} ;
    lyz=${lblsdim#*x} ; ly=${lyz%x*} ;
    lz=${lblsdim##*x} ;

    xd=$(($lx-$x))
    yd=$(($ly-$y))
    zd=$(($lz-$z))

    xr=$(($xd/2))
    yr=$(($yd/2))
    zr=$(($zd/2))

    ifdsntexistrun ${lblsorgnii} "Extracting labels to original size" \
     c3d ${orgortlbls} -region ${xr}x${yr}x${zr} ${alldim} ${lblsorgnii}

    c3d ${inclar} ${lblsorgnii} -copy-transform -o ${lblsorgnii}

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
	antsApplyTransforms -r ${allenhres} -i ${orthresclar} -n Bspline \
	-t [ ${initform}, 1 ] [ ${antsaff}, 1 ] ${antsinvwarp} -o ${regorgclar} --float


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
	antsApplyTransforms -r ${allenhres} -i ${orthresclar} -n Bspline \
	 -t [ ${initform}, 1 ] [ ${antsaff}, 1 ] ${antsinvwarp} -o ${regorgclar} --float

}

#---------------------------

# 5) Create Tiled Mosaic

function createtiledimg()
{
    local smclarres=$1
    local clipped=$2
    local wrplbls=$3
    local rgb_lbls=$4
    local lbl_mask=$5
    local custom_lut=$6
    local mosaic=$7

    # clip clar intensities
    ifdsntexistrun ${clipped} "Clipping CLARITY intensities" \
    c3d ${smclarres} -stretch 2% 98% 0 255 -clip 0 255 -o ${clipped}

    ifdsntexistrun ${lbl_mask} "Making labels mask" \
    ThresholdImage 3 ${wrplbls} ${lbl_mask} 1 inf 1 0

    # create rgb labels
    ifdsntexistrun ${rgb_lbls} "Creating RGB labels" \
    ConvertScalarImageToRGB 3 ${wrplbls} ${rgb_lbls} ${lbl_mask} custom ${custom_lut}

    # create image
    ifdsntexistrun ${mosaic} "Creating tiled mosaic image" \
    CreateTiledMosaic -i ${clipped} -r ${rgb_lbls} -a 0.3 -o ${mosaic} -t -1x7 -f '0x1' -s [10,350,1000] -x ${lbl_mask}

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

    # get brain mask (thresh & largest comp)
    mask=${regdir}/brain_mask.nii.gz
    brain=${regdir}/brain.nii.gz
    sharp=${regdir}/clar_res0.05_sharp.nii.gz
    median=${regdir}/clar_res0.05_median.nii.gz
    biasin=${regdir}/clar_res0.05_median_bias.nii.gz
    otsumaskthr=${regdir}/clar_res0.05_median_bias_otsu_mask_prethr.nii.gz
    otsumask=${regdir}/clar_res0.05_median_bias_otsu_mask.nii.gz
    otsucp=${regdir}/clar_res0.05_median_bias_otsu_precp.nii.gz
    otsu=${regdir}/clar_res0.05_median_bias_otsu.nii.gz

    if [[ ! -f "${otsu}" ]]; then
        getbrainmask ${resclar} ${sharp} ${median} ${brain} ${mask} ${biasin} ${otsumaskthr} ${otsumask} ${otsucp} ${otsu}
    fi

	# Mask
	masclar=${regdir}/clar_res0.05_masked.nii.gz
	maskimage ${resclar} ${otsumask} ${masclar}
#	maskimage ${resclar} ${mask} ${masclar}

    if [[ "${prebias}" == 1 ]]; then
        biasclar=${masclar}
    else
        # N4 bias correct
        biasclar=${regdir}/clar_res0.05_bias.nii.gz
        biasfieldcorr ${masclar} ${biasclar} ${otsumask}

    fi

    # pad image
    padclar=${regdir}/clar_res0.05_pad.nii.gz
    padimage ${biasclar} ${padclar}

	# Orient
	ortclar=${regdir}/clar_res0.05_ort.nii.gz
	orientimg ${padclar} "${ort}" Cubic float ${ortclar}

	# Smooth
	smclar=${regdir}/clar_res0.05_sm.nii.gz
	smoothimg ${ortclar} 0.25 ${smclar}

	# make clarity copy
	clarlnk=${regdir}/clar.nii.gz
	if [[ ! -f "${clarlnk}" ]]; then cp ${smclar} ${clarlnk} ; fi


	#---------------------------


# 2a) initialize registration

	# Allen atlas template

    if [[ "${bulb}" == 0 ]]; then
        allenref=${atlasdir}/ara/template/average_template_25um_OBmasked${side}.nii.gz

    elif [[ "${bulb}" == 1 ]]; then
        allenref=${atlasdir}/ara/template/average_template_25um${side}.nii.gz

    fi


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

	base=`basename ${lbls}`
	lblsname=${base%%.*};

	# Out lbls
	wrplbls=${regdirfinal}/${lblsname}_clar_downsample.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
	swplbls=${regdir}/${lblsname}_ants_swp.nii.gz
	tiflbls=${regdirfinal}/${lblsname}_clar_vox.tif
	reslbls=${regdirfinal}/${lblsname}_clar.nii.gz
	unpadtif=${regdir}/${lblsname}_unpad_clar.tif
	restif=${regdirfinal}/${lblsname}_clar.tif

	smclarres=${regdirfinal}/clar_downsample_res${vox}um.nii.gz

    wrplblsorg=${regdir}/${lblsname}_ants_org.nii.gz
    orgortlbls=${regdir}/${lblsname}_ants_org_ort.nii.gz
    lblsorgnii=${regdirfinal}/${lblsname}_clar_space_downsample.nii.gz

	warpallenlbls ${smclar} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} \
	 ${ortlbls} ${swplbls} ${tiflbls} ${inclar} ${reslbls} ${restif} ${vox} \
	  ${smclarres} ${inclar} ${orgortlbls} ${lblsorgnii} ${wrplblsorg} ${unpadtif}


	#---------------------------


# 4) Warp input CLARITY to Allen


	# ort hres clar
	ortinclar=${regdir}/clar_ort.nii.gz

	# hres Allen
	allenhres=${atlasdir}/ara/template/average_template_10um.nii.gz

	# ants inv warp
	antsinvwarp=${regdir}/allen_clar_ants1InverseWarp.nii.gz

	# out warp hres clar
    regorgclar=${regdirfinal}/clar_allen_space.nii.gz

    if [[ "${warphres}" == 1 ]]; then
        warpinclarallen ${inclar} ${ort} Cubic ushort ${ortinclar} ${allenhres} \
         ${initform} ${antsaff} ${antsinvwarp} ${regorgclar}
    fi

    #---------------------------


# 5) Create Tiled Mosaic

    clipped=${regdir}/clar_downsample_res${vox}um_int_clipped.nii.gz
    custom_lut=${atlasdir}/ara/ara_ants_lut.txt
    rgb_lbls=${regdir}/${lblsname}_clar_downsample_rgb.nii.gz
    lbl_mask=${regdir}/${lblsname}_clar_downsample_mask.nii.gz
    mosaic=${regdirfinal}/allen_labels_to_clar_mosaic.png

    if [[ "${savefig}" == 1 ]]; then
        createtiledimg ${smclarres} ${clipped} ${wrplbls} ${rgb_lbls} ${lbl_mask} ${custom_lut} ${mosaic}
    fi

}


#--------------------

# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

miracl utils end_state -f "Registration and Allen labels warping" -t "$DIFF minutes"


# TODOs
# TODOlp: add settings file to read for pars
