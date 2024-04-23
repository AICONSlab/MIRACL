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

	1) Warps allen annotations or labels in atlas space to the original high-res CLARITY space

	Usage: miracl lbls warp_clar

	A GUI will open to choose your:

			input clarity registration dir

			input Allen Labels to warp (in Allen space)

			file with orientation to standard code (ort2std.txt)

			original / initial clarity tiff folder

			output warped labels 

	----------

	For command-line / scripting

	Usage: miracl lbls warp_clar -r [ clarity registration dir ] -l [ labels in allen space to warp ] -c [ orient file ] 
	-f [ original clarity tiff folder ] -o [ output file name ]

	Example: miracl lbls warp_clar -r clar_reg_allen -l annotation_hemi_combined_25um_grand_parent_level_3.nii.gz -o ort2std.txt 
	-c LSFM_clar_tiff_chan1 -d warped_labels -f annotation_hemi_split_25um_depth6

		arguments (required):

			r. input clarity registration dir

			l. input Allen Labels to warp (in Allen space)

			o. file with orientation to standard code

			c. original clarity tiff folder

			d. output directory 

			f. output warped labels name (tiff files; prefix only without file type '.tif')

		optional arguments:

			i. interpolation (default: MultiLabel ) [ other options: NearestNeighbor ... ]

			t. output file type (default: short) [ other options: char ... ]

	----------		

	Dependencies:
	
		- ANTs
		https://github.com/stnava/ANTs			
		
		- c3d
		https://sourceforge.net/projects/c3d

	-----------------------------------
	
	(c) Maged Goubran @ AICONSlab, 2024
	maged.goubran@utoronto.ca
	
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

c3dpath=`which c3d`
if [ -z ${c3dpath} ]; then
    printf "\n ERROR: c3d not initialized .. please setup miracl & rerun script \n"
	exit 1
else
	printf "\n c3d path check: OK... \n"
fi

#----------
# Init atlas dir
atlasdir=${MIRACL_HOME}/atlases


# GUI for CLARITY input imgs
function choose_folder_gui()
{
	local openstr=$1
	local _inpath=$2

	${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f folder -s "$openstr"
	
	filepath=`cat path.txt`
	
	eval ${_inpath}="'$filepath'"

	rm path.txt

}

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

	${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f file -s "$openstr"

	filepath=`cat path.txt`

	eval ${_inpath}="'$filepath'"

	rm path.txt

}

# Select Mode : GUI or script
if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":r:l:c:f:o:d:i:t:" opt; do
	    case "${opt}" in
	        r)
	            regdir=${OPTARG}
	            ;;
	        l)
	            lbls=${OPTARG}
	            ;;
	        o)
	            ortfile=${OPTARG}
	            ;;
	        c)
	            clardir=${OPTARG}
	            ;;
	        f)
	            outputname=${OPTARG}
	            ;;
	        d)
	            outputdir=${OPTARG}
	            ;;
	        i)
	            interpolation=${OPTARG}
	            ;;
	        t)
	            outputtype=${OPTARG}
	            ;;
	        *)
	            usage
	            ;;
	    esac
	done



	# check required input arguments
	if [ -z ${regdir} ];
	then
		usage
		echo "ERROR: < -r => input clarity registration dir > not specified"
		exit 1
	fi

    if [ -z ${lbls} ];
	then
		usage
		echo "ERROR: < -l => labels > not specified"
		exit 1
	fi

	if [ -z ${ortfile} ];
	then
		usage
		echo "ERROR: < -c => orient code file > not specified"
		exit 1
	fi

	if [ -z ${clardir} ];
	then
		usage
		echo "ERROR: < -f => input original clarity dir > not specified"
		exit 1
	fi

	if [ -z ${outputdir} ];
	then
		usage
		echo "ERROR: < -d => outputdir > output directory not specified"
		exit 1
	fi

	if [ -z ${outputname} ];
	then
		usage
		echo "ERROR: < -o => outputname > output file name not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_folder_gui "Clarity registration folder" regdir

	choose_file_gui "Input labels to warp" lbls

	choose_file_gui "Input orient file" ortfile

	choose_folder_gui "Clarity registration folder" clardir

	choose_folder_gui "Output directory" outputdir

	choose_file_gui "Output file name" outputname 	# file name 

	# check required input arguments
	if [ -z ${regdir} ] || [ -z ${lbls} ] || [ -z ${ortfile} ] || [ -z ${clardir} ] || [ -z ${outputname} ] || [ -z ${outputdir} ]; then
	    usage
	    echo "ERROR: Required arguments are missing."
	    exit 1
	fi

fi

# get time
START=$(date +%s)

# output log file of script
exec > >(tee -i ${regdir}/clar_allen_lbls_warp_script.log)
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


#---------------------------
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
	# local orttaglbls=$7
	local regdir=$7
	local ortintlbls=$8
	local orttypelbls=$9
	local ortlbls=${10}

	# swap lbls
	local swplbls=${11}
	local tiflbls=${12}

	# Up lbls
    local inclar=${13}
    local reslbls=${14}
    local outputname=${15}

    # Vox
    local vox=${16}

    # Res clar
    local smclarres=${17}

    # lbls to high res tiff
    local orgclar=${18}
    local tiflblszstack=${19}
    local tifdirreg=${20}
    local tifdirregfinal=${21}
    local lblsname=${22}


    # Upsample ref
    vres=`python -c "print(${vox}/1000.0)"`


    # res clar in
    ifdsntexistrun ${smclarres} "Usampling reference image" ResampleImage 3 ${smclar} ${smclarres} ${vres}x${vres}x${vres} 0 1

	# warp to registered clarity
	ifdsntexistrun ${wrplbls} "Applying ants deformation to Allen labels" \
	 antsApplyTransforms -r ${smclarres} -i ${lbls} -n Multilabel -t ${antswarp} ${antsaff} ${initform} -o ${wrplbls}

	# orient to org
	# ifdsntexistrun ${ortlbls} "Orienting Allen labels" orientimg ${wrplbls} ${orttaglbls} ${ortintlbls} ${orttypelbls} ${ortlbls}

	# get org tag
	inclar=${regdir}/clar_res0.05.nii.gz
	ortmatrix=`PrintHeader ${inclar} 4 | tr 'x' ' '`
	ifdsntexistrun ${ortlbls} "Orienting Allen labels" SetDirectionByMatrix ${wrplbls} ${ortlbls} ${ortmatrix}

	# swap dim (x=>y / y=>x)
	ifdsntexistrun ${swplbls} "Swapping label dimensions" PermuteFlipImageOrientationAxes 3 ${ortlbls} ${swplbls}  1 0 2  1 0 0

	# create tif lbls
	# ifdsntexistrun ${tiflbls} "Converting lbls to tif" c3d ${swplbls} -type ${orttypelbls} -o ${tiflbls}


    padvox=11.5

    printf "\n pad vox: ${padvox} \n" 

    ifdsntexistrun ${tiflbls} "Un-padding high res tif" c3d ${swplbls} -type ${orttypelbls} -pad -${padvox}% -${padvox}% -o ${tiflbls}

    # create hres tif lbls

    # get tiflbls dim
    tiflblsdim=`PrintHeader ${tiflbls} 2`
    tiflblsx=${tiflblsdim%%x*} ;
    tiflblsyz=${tiflblsdim#*x} ; tiflblsy=${tiflblsyz%x*} ;
    # z=${tiflblsdim##*x} ;

    # get num slices (z dim)
	orgclar=$(realpath ${orgclar})
	orgclarz=`ls ${orgclar}/*.tif* | wc -l` 
	firstslice=${orgclar}/`ls ${orgclar} | head -n1`

    # get first_slice dim
    firstslicedim=`PrintHeader ${firstslice} 2`
    firstslicex=${firstslicedim%%x*} ;
    firstslicey=${firstslicedim##*x} ;


    printf "\n orgclar: ${orgclar} \n" 
	printf "\n orgclar z: ${orgclarz} \n"

    ifdsntexistrun ${tiflblszstack} "Resampling high res tif" ResampleImage 3 ${tiflbls} ${tiflblszstack} ${tiflblsx}x${tiflblsy}x${orgclarz} 1 1 3  
    # 1- Spacing , 1- NN, 3- ushort

	if [[ ! -d ${tifdirreg} ]]; then
    	mkdir -p ${tifdirreg} ${tifdirregfinal} 
    fi  


    firstlbl=${tifdirreg}/lbls_slice_000000.tif

    ifdsntexistrun ${firstlbl} "Extracting tiff slices" c3d ${tiflblszstack} -slice z 0:-1 -type ushort -oo ${tifdirreg}/lbls_slice_%06d.tif

    loop_z=$(python -c "print(${orgclarz}-1)")


    firstlblclar=${tifdirregfinal}/${lblsname}_000000.tif

    printf "\n firstslice: ${firstslice} \n" 
    printf "\n firstslice x: ${firstslicex} \n"
    printf "\n firstslice y: ${firstslicey} \n"

    # printf "\n loop z: ${loop_z} \n" 

    if [[ ! -f ${firstlblclar} ]]; then

    	printf "\n Resampling tiff slices to original space \n"

		for i in $(seq 0 ${loop_z}); 
			do 
				i=$(printf %06d $i) ; 
				ResampleImage 2 ${tifdirreg}/lbls_slice_${i}.tif ${tifdirregfinal}/${outputname}_${i}.tif ${firstslicex}x${firstslicey} 1 1 3 ; 
		done

	fi



	# ifdsntexistrun ${restif} "Generating high res lbls in tif" \
		# ResampleImage 3 ${swplbls} ${restif} ${x}x${y}x${z} 1 1 0
	
	 # c3d ${swplbls} -resample ${x}x${y}x${z}mm -interpolation ${ortintlbls} -type ${orttypelbls} -o ${restif}

	# ifdsntexistrun ${restif} "Converting high res lbls to tif" \ 
	# c3d ${swplbls} -resample ${ox}x${oy}x${z}mm -interpolation ${ortintlbls} -type ${orttypelbls} -o ${restif}

}

#---------------------------
# Build main function

function main()
{

	# Print final args to screen for user
	printf "\n ######################################################\n"
	printf "\n The following arguments will be used for label warping:"
	printf "\n r: Registration dir: ${regdir}\n"
	printf "\n c: Clarity tiff folder: ${clardir}\n"
	printf "\n d: Output directory: ${outputdir}\n"
	printf "\n o: Orientation code: ${ortfile}\n"
	printf "\n f: Output file name: ${outputname}\n"
	printf "\n i: Interpolation: ${interpolation}\n"
	printf "\n t: Output type: ${outputtype}\n"
	printf "\n ######################################################\n"


# Set default values for optional arguments if not provided
	interpolation=${interpolation:-"MultiLabel"}
	outputtype=${outputtype:-"ushort"}

# 1) Warp Allen labels to original CLARITY

	regdir=$(realpath ${regdir})
	motherdir=$(dirname ${regdir})

    regdirfinal=${motherdir}/reg_final

    # regdirfinal=$PWD/reg_final

    if [[ ! -d ${regdirfinal} ]]; then

        printf "\n Creating registration folder\n"
        mkdir -p ${regdirfinal}

    fi

	# Tforms
	initform=${regdir}/init_tform.mat
	antswarp=${regdir}/allen_clar_ants1Warp.nii.gz
	antsaff=${regdir}/allen_clar_ants0GenericAffine.mat

	base=`basename ${outputname}`
	lblsname=${base%%.*};

    # In files
    smclar=${regdir}/clar.nii.gz

    # last file made in niftis folder
    inclar=`ls -r ${motherdir}/niftis/*down* | tail -n 1`

    # printf "inclar: ${inclar}"

    # Out lbls
	wrplbls=${regdirfinal}/${lblsname}_clar_downsample.nii.gz
	ortlbls=${regdir}/${lblsname}_ants_ort.nii.gz
	swplbls=${regdir}/${lblsname}_ants_swp.tif
	tiflbls=${regdir}/${lblsname}_clar_vox.tif
	reslbls=${regdir}/${lblsname}_clar.nii.gz

	# restif=${regdirfinal}/${lblsname}_clar.tif

    lblsdim=`PrintHeader ${lbls} 1`
    xlbl=${lblsdim%%x*}

    vox=`python -c "print (${xlbl}*1000.0)"`

	smclarres=${regdirfinal}/clar_downsample_res${vox}um.nii.gz

    ort=`cat ${ortfile} | grep ortcode | cut -d = -f 2`

    tiflblszstack=${regdir}/${lblsname}_unpad_clar_zstack.tif
    tifdirreg=${regdir}/${lblsname}_tiff
    tifdirregfinal=${outputdir}/${lblsname}_tiff_clar


	warpallenlbls ${smclar} ${lbls} ${antswarp} ${antsaff} ${initform} ${wrplbls} ${regdir} ${interpolation} ${outputtype} \
		${ortlbls} ${swplbls} ${tiflbls} ${inclar} ${reslbls} ${outputname} ${vox} ${smclarres} \
		${clardir} ${tiflblszstack} ${tifdirreg} ${tifdirregfinal} ${lblsname} ${regdir}


}

#--------------------
# call main function
main

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Label warping done in $DIFF minutes. Have a good day!"
