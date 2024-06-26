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

    Workflow (wrapper) combining multiple MIRACL functions:

    1) Sets orientation of input data using a GUI
    2) Converts TIFF to NII
	3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
	4) Warps Allen annotations to the original high-res CLARITY space
	5) Warps the higher-resolution CLARITY to Allen space

    Executes:
        conv/miracl_conv_set_orient_gui.py (if run in GUI mode)
        conv/miracl_conv_convertTIFFtoNII.py
        reg/miracl_reg_clar-allen.sh

    Usage: miracl flow reg_clar

        A GUI will open to set data orientation
        For "miracl_conv_convertTIFFtoNII.py" & "miracl_reg_clar-allen.sh" default parameters will be chosen

    ----------
	For command-line / scripting

    Usage: miracl flow reg_clar -f [Tiff folder]
    Example: miracl flow reg_clar -f my_tifs -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

        arguments (required):
            f. Input Clarity tif dir/folder

        optional arguments (remember the quotes):
            w.  output directory (default: working directory)

            conversion to nii (invoked by -n " "):
            d.  [ Downsample ratio (default: 5) ]
            cn. [ chan # for extracting single channel from multiple channel data (default: 1) ]
            cp. [ chan prefix (string before channel number in file name). ex: C00 ]
            ch. [ output chan name (default: eyfp) ]
            vx. [ original resolution in x-y plane in um (default: 5) ]
            vz. [ original thickness (z-axis resolution / spacing between slices) in um (default: 5) ]
            c.  [ nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

            Registration (invoked by -r " "):
            o.  Orient code (default: ALS)
                to orient nifti from original orientation to "standard/Allen" orientation
            m.  Warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
                accepted inputs are: <split> or <combined>  (default: combined)
            v.  Labels voxel size/Resolution of labels in um
                accepted inputs are: 10, 25 or 50  (default: 10)
            l.  image of input Allen Labels to warp (default: annotation_hemi_split_10um.nii.gz - which are at a resolution of 0.01mm/10um)
                input could be at a different depth than default labels
                If l. is specified (m & v cannot be specified)
            a.  input custom Allen atlas (for example for registering sections)
            s.  side, if only registering a hemisphere instead of whole brain
                accepted inputs are: rh (right hemisphere) or lh (left)

	----------
	Main Outputs

        reg_final/clar_allen_space.nii.gz: Clarity data in Allen reference space
        reg_final/clar_downsample_res(vox)um.nii.gz : Clarity data downsampled and oriented to "standard"
        reg_final/annotation_hemi_(hemi)_(vox)um_clar_downsample.nii.gz : Allen labels registered to downsampled Clarity
        reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif : Allen labels registered to oriented Clarity
        reg_final/annotation_hemi_(hemi)_(vox)um_clar.tif : Allen labels registered to original (full-resolution) Clarity

        - To visualize results use: miracl reg check
        - Full resolution Allen labels in original clarity space (.tif) can be visualized by Fiji

	-----------------------------------

usage
getversion >&2

}


# Call help/usage function
if [[ "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then

    usage >&2
    exit 1

fi


#----------------------

# check dependencies

if [[ -z ${MIRACL_HOME} ]];
then

    printf "\n ERROR: MIRACL not initialized .. please run init/setup_miracl.sh  & rerun script \n"
	exit 1

fi

c3dpath=`which c3d`
if [[ -z ${c3dpath} ]];
then
    abspath_pwd="$( cd "$(dirname "$0")" ; pwd -P )"
    c3dpath="${abspath_pwd}/../../depends/c3d/bin"
    export PATH="$PATH:${abspath_pwd}/../../depends/c3d/bin"
fi

test_c3dpath=`which c3d`
if [[ -z ${test_c3dpath} ]];
then
    printf "\n ERROR: c3d not initialized .. please setup miracl & rerun script \n"
	exit 1
else
	printf "\n c3d path check: OK... \n"
fi

#----------------------

# get time

START=$(date +%s)

#---------------------------
#---------------------------


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

    printf "\n Reading input parameters \n"

	while getopts ":f:w:o:n:r:" opt; do

	    case "${opt}" in

            f)
            	indir="${OPTARG}"
            	;;

            w)
            	work_dir="${OPTARG}"
            	;;

            o)
            	ort="${OPTARG}"
            	;;

            n)
            	convopts="${OPTARG}"
            	;;

        	r)
            	regopts="${OPTARG}"
            	;;

        	*)
            	usage
            	;;

		esac

	done


	# check required input arguments

	if [[ -z ${indir} ]];
	then
		usage
		echo "ERROR: < -f => input folder with clarity tifs> not specified"
		exit 1
	fi

    # make reg dir
    if [[ -z "${work_dir}" ]] || [[ "${work_dir}" == "None" ]]; then

        work_dir=${PWD}
        regdirfinal=${PWD}/reg_final
        regdir=${PWD}/clar_allen_reg

    else

        regdirfinal=${work_dir}/reg_final
        regdir=${work_dir}/clar_allen_reg

    fi

    if [[ ! -d ${regdir} ]]; then

        printf "\n Creating registration folder\n"
        mkdir -p "${regdirfinal}" "${regdir}"

    fi

    # output log file of script

    exec > >(tee -i ${regdir}/workflow_reg_clar_allen.log)
    exec 2>&1


    #---------------------------
    # Call conversion to nii

    printf "\n Running Tiff to Nii conversion with the following command: \n"

    if [[ -z "${convopts}" ]];
	then

        printf "\n miracl conv tiff_nii -f "${indir}" \n"
        # miracl_conv_convertTIFFtoNII.py -f ${indir}
        miracl conv tiff_nii -f "${indir}" -w "${work_dir}"

    else

        printf "\n miracl conv tiff_nii -f "${indir}" ${convopts} \n"
        # miracl_conv_convertTIFFtoNII.py -f ${indir} ${convopts}
        miracl conv tiff_nii -f "${indir}" -w "${work_dir}" ${convopts}

    fi

    #---------------------------
    # Call registration

    printf "\n Running CLARITY registration to Allen with the following command: \n"

    # last file made in niftis folder
    nii=`ls ${work_dir}/niftis | tail -n 1`

    if [[ -z "${regopts}" ]];
	then

        printf "\n miracl reg clar_allen -i niftis/${nii} \n"
        miracl reg clar_allen -i ""${work_dir}"/niftis/"${nii}"" -w "${work_dir}"

    else

        printf "\n miracl reg clar_allen -i niftis/${nii} ${regopts} \n"
        miracl reg clar_allen --i ""${work_dir}"/niftis/"${nii}"" -w "${work_dir}" ${regopts}

    fi

    #---------------------------
    #---------------------------

else

	# call gui
	printf "\n No inputs given ... running in GUI mode \n"

    #---------------------------
    # Call set orient GUI

    printf "\n Running Set orient with the following command: \n"

    printf "\n miracl conv set_orient \n"
    miracl conv set_orient

    indir=`cat ort2std.txt | grep tifdir | cut -d '=' -f 2`

    # check required input arguments

	if [[ -z ${indir} ]];
	then
		usage
		echo "ERROR: input CLARITY dir not specified"
		exit 1
	fi


    # output log file of script

    exec > >(tee -i ${regdir}/workflow_reg_clar_allen.log)
    exec 2>&1

    #---------------------------
    # Get nii conv opts

    # options gui Nii conv
	opts=$(${MIRACL_HOME}/conv/miracl_conv_gui_options.py -t "Nii conversion options" \
	-d "output directory (def = working dir)" -f "out nii (def = clarity)" "downsample ratio (def = 5)" \
	 "channel #" "channel prefix" "channel name (def = eyfp)" "in-plane res (def = 5 um)" \
    "z res (def = 5 um)" "center (def = 0 0 0)"  -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

    work_dir="$(echo -e "${arr[0]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    # outnii=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    if [[ -z ${work_dir} ]]; then work_dir=$PWD ; fi
    printf "\n Chosen working dir: $work_dir \n"

    outnii="$(echo -e "${arr[1]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${outnii} ]]; then outnii="clarity" ; fi
    printf "\n Chosen out nii name: $outnii \n"

    d="$(echo -e "${arr[2]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${d} ]]; then d=5 ; fi
    printf "\n Chosen downsample ratio: $d \n"

    chann="$(echo -e "${arr[3]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${chann} ]]; then chann=0 ; fi
    printf "\n Chosen channel #: $chann \n"

    chanp="$(echo -e "${arr[4]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    printf "\n Chosen channel prefix: $chanp \n"

    chan="$(echo -e "${arr[5]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${chan} ]]; then chan="eyfp" ; fi
    printf "\n Chosen out channel name: $chan \n"

    vx="$(echo -e "${arr[6]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${vx} ]]; then vx=5 ; fi
    printf "\n Chosen in-plane res: $vx \n"

    vz="$(echo -e "${arr[7]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${vz} ]]; then vz=5 ; fi
    printf "\n Chosen thickness: $vz \n"

    cent="$(echo -e "${arr[8]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${cent} ]]; then cent="0 0 0" ; fi
    printf "\n Chosen image center: $cent \n"


    #---------------------------
    # Get reg opts

    # options gui for Reg
	regopts=$(${MIRACL_HOME}/conv/miracl_conv_gui_options.py -t "Reg options" \
	        -f "Hemi [combined (def)/split]" "Labels resolution [vox] (def = 10 'um')" "olfactory bulb incl. (def = 0)" \
	         "side [blank (def) / rh / lh]" -v "input custom atlas [blank (def)]" "input custom labels [blank (def)]" \
	          -hf "`usage`")

	# populate array
	regarr=()
	while read -r line; do
	   regarr+=("$line")
	done <<< "$regopts"


	hemi="$(echo -e "${regarr[0]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${hemi} ]]; then hemi="combined" ; fi
	printf "\n Chosen hemi: ${hemi} \n"

	vox="$(echo -e "${regarr[1]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${vox} ]]; then vox=10 ; fi
	printf "\n Chosen vox (um): ${vox} \n"

	ob="$(echo -e "${regarr[2]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${ob} ]]; then ob=0 ; fi
    printf "\n Chosen ob: ${ob} \n"

	side="$(echo -e "${regarr[3]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${side} ]]; then side="" ; fi
    printf "\n Chosen ob: ${side} \n"

	side="$(echo -e "${regarr[3]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${side} ]]; then side="" ; fi
    printf "\n Chosen ob: ${side} \n"

	atlas="$(echo -e "${regarr[4]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${atlas} ]]; then atlas="" ; fi
    printf "\n Chosen custom atlas: ${atlas} \n"

	lbls="$(echo -e "${regarr[5]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z ${lbls} ]]; then lbls="" ; fi
    printf "\n Chosen custom atlas: ${lbls} \n"

    # make reg dir
    regdirfinal=${work_dir}/reg_final
    regdir=${work_dir}/clar_allen_reg

    if [[ ! -d ${regdir} ]]; then

        printf "\n Creating registration folder\n"
        mkdir -p ${regdirfinal} ${regdir}

    fi

    #---------------------------
    # Call conversion to nii

    printf "\n Running Tiff to Nii conversion with the following command: \n"

    if [[ -z ${chanp} ]]; then

        printf "\n miracl conv tiff_nii -f ${indir} -w ${work_dir}  -o ${outnii} -d ${d} -ch ${chan} -vx ${vx} -vz ${vz} -c ${cent} \n"
        miracl conv tiff_nii -f ${indir} -w "${work_dir}" -o ${outnii} -d ${d} -ch ${chan} -vx ${vx} -vz ${vz} -c ${cent}

    else

        printf "\n miracl conv tiff_nii -f ${indir} -w ${work_dir} -o ${outnii} -d ${d} -cn ${chann} -cp ${chanp} -ch ${chan} -vx ${vx} -vz ${vz} -c ${cent} \n"
        miracl conv tiff_nii -f ${indir} -w "${work_dir}"  -o ${outnii} -d ${d} -cn ${chann} -cp ${chanp} -ch ${chan} -vx ${vx} -vz ${vz} -c ${cent}

    fi


    #---------------------------
    # Call registration

    printf "\n Running CLARITY registration to Allen with the following command: \n"

    # last file made in niftis folder
    nii=`ls ${work_dir}/niftis | tail -n 1`

    ort=`cat ${work_dir}/ort2std.txt | grep ortcode | cut -d '=' -f 2`
    ort="${ort:0:3}"

    printf "\n miracl reg clar_allen -i niftis/${nii} -w ${work_dir} -o ${ort} -m ${hemi} -v ${vox} -b ${ob} -s ${side} -a ${atlas} -l ${lbls} -c ${indir}\n"
    miracl reg clar_allen -i ""${work_dir}"/niftis/"${nii}"" -w "${work_dir}" -o "${ort}" -m "${hemi}" -v "${vox}" -b "${ob}" -s "${side}" -a "${atlas}" -l "${lbls}" -c "${indir}"

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

miracl utils end_state -f "Conversion, Registration and Allen labels warping" -t "$DIFF minutes"