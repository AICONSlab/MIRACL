#!/bin/bash

# get version
function getversion() {
  ver=$(cat "$MIRACL_HOME"/version.txt)
  printf "\n MIRACL pipeline v%s \n" "$ver"
}

# help/usage function
function usage() {

  cat <<usage

	1) Registers in-vivo or ex-vivo MRI data to Allen/Dsurqe Reference mouse brain or Fischer/Waxholm Reference rat brain Atlas
	2) Warps Allen/Dsurqe/Fischer/Waxholm annotations to the MRI space

	if no inputs are given function will run in GUI mode

	For command-line / scripting

	Usage: miracl reg mri_allen_nifty -i [ input invivo or exvivo MRI nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -b [ olfactory bulb ] -s [ skull strip ] -n [ no orient needed ] -a [ atlas ] -e [ bending energy ] -x [ grid spacing x-axis ]

    Example: miracl reg mri_nifty -i inv_mri.nii.gz -o RSP -m combined -v 25

    arguments (required):
        i.  input MRI nii
            Preferably T2-weighted

    optional arguments:
        r.  set base dir for reg output (default: cwd)
        o.  orient code (default: RSP)
            to orient nifti from original orientation to 'standard/Allen/Fischer/Dsurqe/Waxholm' orientation
        a.  atlas (default: allen)
            use 'allen' or 'dsurqe' for mouse models and 'fischer' or 'waxholm' atlas for rat models
            accepted inputs are: <allen>, <dsurqe>, <fischer> or <waxholm>
        l.  input atlas labels to warp (default: annotation_hemi_combined_10um.nii.gz - for Allen atlas)
            input labels could be at a different depth than default labels
        f.  FSL skull striping fractional intensity (default: 0.3), smaller values give larger brain outlines
        n.  no orientation needed (input image in 'standard' orientation), binary option (default: 0 -> orient)
        s.  skull strip or not, binary option (default: 1 -> skull-strip)
        e.  weight of the bending energy (second derivative of the transformation) penalty term (default: 1e-3)
        x.  final grid spacing along the x axis in mm (in voxel if negative value) (default: -15)

    Allen atlas related arguments:
        m.  hemisphere mirror (default: combined)
            warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
            accepted inputs are: <split> or <combined>
        v.  labels voxel size/Resolution in um (default: 10)
            accepted inputs are: 10, 25 or 50
            If l. is specified (m & v cannot be specified)
        b.  olfactory bulb included in brain, binary option (default: 0 -> not included)

	-----------------------------------
	registration based on NiftyReg
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

if [ -z "${MIRACL_HOME}" ]; then
  printf "\n ERROR: MIRACL not initialized. Please run init/setup_miracl.sh & rerun script \n"
  exit 1
fi

fslcmd=$(which fsl)
if [ -z "${fslcmd// /}" ]; then
  echo "ERROR: < FSL not initialized .. please intall it & run init/check_depend.sh > not specified"
  exit 1
fi

c3dpath=$(which c3d)
if [ -z "${c3dpath}" ]; then
  printf "\n ERROR: c3d not initialized .. please setup miracl & rerun script \n"
  exit 1
fi

#----------

# Init atlas dir

# atlasdir=${MIRACL_HOME}/atlases
atlasdir=${ATLASES_HOME}

# GUI for MRI input imgs

function choose_file_gui() {
  local openstr=$1
  local ftype=$2
  local _inpath=$3

  filepath=$("${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py" -f file -s "$openstr" -t "$ftype")

  filepath=$(echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  #	filepath=`cat path.txt`

  eval "${_inpath}"="'$filepath'"

  #	rm path.txt

}

# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

  printf "\n Running in script mode \n"

  while getopts ":i:r:o:l:m:v:b:s:f:n:a:e:x:" opt; do

    case "${opt}" in

    i)
      inmr=${OPTARG}
      ;;
    r)
      work_dir=${OPTARG}
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
    a)
      atl=${OPTARG}
      ;;
    e)
      be=${OPTARG}
      ;;
    x)
      sx=${OPTARG}
      ;;
    *)
      usage
      ;;

    esac

  done

  # check required input arguments

  if [ -z "${inmr}" ]; then
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
  opts=$("${MIRACL_HOME}/conv/miracl_conv_gui_options.py" -t "Reg options" -v "In-vivo or Ex-vivo MRI" \
    -f "Orient code (def = RSP)" "Labels Hemi [combined (def)/split]" "Labels resolution [vox] (def = 10 'um')" \
    "olfactory bulb incl. (def = 0)" "skull strip (def = 1)" "No orient (def = 0)" "atlas (def = allen)" -hf "$(usage)")

  # populate array
  arr=()
  while read -r line; do
    arr+=("$line")
  done <<<"$opts"

  inmr=$(echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  # check required input arguments

  if [[ -z ${inmr} ]] || [[ "${inmr}" == "No file was chosen" ]]; then
    usage
    echo "ERROR: <input MRI nii> was not chosen"
    exit 1
  fi

  printf "\n Input file path: %s \n" "${inmr}"

  ort=$(echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen orient code: %s \n" "$ort"

  hemi=$(echo "${arr[2]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen labels hemi option: %s \n" "$hemi"

  vox=$(echo "${arr[3]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen vox (um): %s \n" "$vox"

  bulb=$(echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen olfactory bulb option: %s \n" "$bulb"

  skull=$(echo "${arr[5]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen skull strip option: %s \n" "$skull"

  noort=$(echo "${arr[6]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen No orientation option: %s \n" "$noort"

  atl=$(echo "${arr[7]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//')

  printf "\n Chosen atlas: %s \n" "$atl"

fi

# atlas type
if [[ -z ${atl} || ${atl} == "None" ]]; then

  atl=allen

else

  if [ "${atl}" != "allen" ] && [ "${atl}" != "fischer" ] && [ "${atl}" != "dsurqe" ] && [ "${atl}" != "waxholm" ]; then

    printf "ERROR: < -a => (atl) > only takes as inputs: allen, dsurqe, fischer or waxholm"
    exit 1

  fi

fi

# make reg dir
if [[ -z ${work_dir} ]] || [[ "${work_dir}" == "None" ]]; then

  regdirfinal=${PWD}/reg_final
  regdir=${PWD}/clar_${atl}_reg

else

  regdirfinal=${work_dir}/reg_final
  regdir=${work_dir}/clar_${atl}_reg

fi

if [[ ! -d ${regdir} ]]; then

  printf "\n Creating registration folder\n"
  mkdir -p "${regdirfinal}" "${regdir}"

fi

# output log file of script
exec > >(tee -i "${regdir}/mri_'${atl}'_script.log")
exec 2>&1

#---------------------------

# set defaults and assert (check for input errors)

# orient code
if [[ -z ${ort} ]]; then
  ort=RSP
fi

# Check if be or sx are empty, null, or None, and set to default if so
if [[ -z "$be" || "$be" == "null" || "$be" == "None" ]]; then
  be=1e-3
fi

if [[ -z "$sx" || "$sx" == "null" || "$sx" == "None" ]]; then
  sx=-15
fi

# Add default for $hemi to prevent script from failing if no arg is provided by user
# FYI, parameter expansion only sets the default if $hemi is unset or null
: "${hemi:=combined}"

# Also check for None
if [ "$hemi" = "None" ]; then
  hemi="combined"
fi

# If want to warp multi-res / hemi lbls
if [ "${atl}" == "allen" ]; then

  if [[ -z ${lbls} || ${lbls} == "None" ]]; then

    if [[ -z ${hemi} || ${hemi} == "None" ]]; then

      hemi=combined

    else

      if [ "${hemi}" != "combined" ] && [ "${hemi}" != "split" ]; then

        printf "ERROR: < -m => (hemi) > only takes as inputs: combined or split"
        exit 1
      fi

    fi

    if [[ -z ${vox} || ${vox} == "None" ]]; then

      vox=10

    else

      if [ "${vox}" != 10 ] && [ "${vox}" != 25 ] && [ "${vox}" != 50 ]; then

        printf "ERROR: < -v => (vox) > only takes as inputs: 10, 25 or 50"
        exit 1
      fi

    fi

    lbls=${atlasdir}/ara/annotation/annotation_hemi_${hemi}_${vox}um.nii.gz

  fi

elif [ "${atl}" == "fischer" ]; then

  vox=60
  lbls=${atlasdir}/fischer/annotation/Fischer344_template_labels.nii.gz

elif [ "${atl}" == "dsurqe" ]; then

  vox=40
  lbls=${atlasdir}/dsurqe/annotation/DSURQE_40micron_labels.nii.gz

elif [ "${atl}" == "waxholm" ]; then

  vox=39
  lbls=${atlasdir}/waxholm/annotation/WHS_SD_rat_atlas_v4.nii.gz

else
  printf "ERROR: < -a => (atl) > Only accepted atlases (inputs) are: 'allen', 'fischer', 'dsurqe' or 'waxholm'"
  exit 1
fi

# no orient
if [[ -z ${noort} || ${noort} == "None" ]]; then
  noort=0
else

  if [ "${noort}" != 0 ] && [ "${noort}" != 1 ]; then

    printf "ERROR: < -n = > (noort) > only takes as inputs: 0 or 1"
    exit 1

  fi
fi

# skull strip
if [[ -z ${skull} || ${noort} == "None" ]]; then
  skull=1
else

  if [ "${skull}" != 0 ] && [ "${skull}" != 1 ]; then

    printf "ERROR: < -s = > (skull) > only takes as inputs: 0 or 1"
    exit 1

  fi

fi

# olfactory bulb
# FIX: What if Fischer is used here?
if [[ -z ${bulb} || ${bulb} == "None" ]]; then
  bulb=0
else

  if [ "${bulb}" != 0 ] && [ "${bulb}" != 1 ]; then

    printf "ERROR: < -b = > (bulb) > only takes as inputs: 0 or 1"
    exit 1

  fi
fi

# fractional intensity for skull-strip
if [[ -z ${frac} || ${frac} == "None" ]]; then
  frac=0.3
fi

# get time

START=$(date +%s)

#---------------------------
#---------------------------

# 1) Process MRI Functions

# Function to check if file exists then runs other command

function ifdsntexistrun() {

  local outfile="$1"
  local outstr="$2"
  local fun="${@:3}"

  if [[ ! -f ${outfile} ]]; then

    printf "\n %s \n" "$outstr"
    echo "$fun"
    eval "${fun}"

  else

    printf "\n %s already exists ... skipping \n" "$outfile"

  fi

}

# N4 bias correct

function biasfieldcorr() {

  local unbiasmr=$1
  local biasmr=$2

  ifdsntexistrun "${biasmr}" "Bias-correcting MRI image with N4" N4BiasFieldCorrection -d 3 -i "${unbiasmr}" -s 2 -o "${biasmr}"

}

# Remove outline w erosion & dilation

# Thr

function thresh() {

  local biasmr=$1
  local thr=$2
  local thrmr=$3

  #	ifdsntexistrun $thrmr "Thresholding MRI image" c3d $biasmr -threshold ${p1}% ${p2}% $t1 $t2 -o $thrmr
  ifdsntexistrun "${thrmr}" "Thresholding MRI image" fslmaths "${biasmr}" -thrP "${thr}" "${thrmr}"

}

# Crop to smallest roi

function croptosmall() {

  local thrmr=$1
  local cropmr=$2

  dims=$(fslstats "${thrmr}" -w)

  #	ifdsntexistrun ${cropmr} "Cropping MRI image to smallest ROI" c3d $smmr -trim ${trim}vox -type short -o $mrroi
  ifdsntexistrun "${cropmr}" "Cropping MRI image to smallest ROI" fslroi "${thrmr}" "${cropmr}" "${dims}"

}

# change header * 10 dims

function mulheader() {

  local unhdmr=$1
  local mulfac=$2
  local hdmr=$3

  dim1=$(fslinfo "${unhdmr}" | grep pixdim1)
  x=${dim1##*1 }
  dim2=$(fslinfo "${unhdmr}" | grep pixdim2)
  y=${dim2##*2 }
  dim3=$(fslinfo "${unhdmr}" | grep pixdim3)
  z=${dim3##*3 }

  nx=$(echo "${x}"*"${mulfac}" | bc)
  ny=$(echo "${y}"*"${mulfac}" | bc)
  nz=$(echo "${z}"*"${mulfac}" | bc)

  ifdsntexistrun "${hdmr}" "Altering MRI header" c3d "${unhdmr}" -spacing "${nx}"x"${ny}"x"${nz}"mm -o "${hdmr}"

}

# skull strip

function skullstrip() {

  local skullmr=$1
  local betmr=$2
  local frac=$3

  com=$(fslstats "${skullmr}" -C)

  #    ifdsntexistrun ${betmr} "Skull stripping MRI image" bet ${skullmr} ${betmr} -r 55 -c ${com} -f ${frac}

  ifdsntexistrun "${betmr}" "Skull stripping MRI image" bet "${skullmr}" "${betmr}" -c "${com}" -f "${frac}" -R

}

# Orient

function orientimg() {

  local unortmr=$1
  local orttag=$2
  local ortint=$3
  local orttype=$4
  local ortmr=$5

  ifdsntexistrun "${ortmr}" "Orienting MRI to standard orientation" \
    c3d "${unortmr}" -orient "${orttag}" -interpolation "${ortint}" -type "${orttype}" -o "${ortmr}"

}

# Smooth image

function smoothimg() {

  local ortmr=$1
  local sigma=$2
  local smmr=$3

  ifdsntexistrun "$smmr" "Smoothing MRI image" SmoothImage 3 "$ortmr" "${sigma}" "$smmr" 0 1
  #    ifdsntexistrun ${smmr} "Smoothing MRI image" c3d ${ortmr} -smooth ${sigma}x${sigma}x${sigma}mm -o ${smmr}

}

#---------------------------

# 2a) initialize registration Function

#---------------------------

# 2b) Register to Allen atlas Function

#---------------------------

# 3) Warp Allen labels to original MRI Function

#---------------------------

# 4) Warp MRI to Allen space Function

#---------------------------

# Build main function

function main() {

  # 1) Process MRI

  # N4 bias correct
  biasmr=${regdir}/mr_bias.nii.gz
  biasfieldcorr "${inmr}" "${biasmr}"

  # Thr
  thrmr=${regdir}/mr_bias_thr.nii.gz
  thresh "${biasmr}" 40 "${thrmr}"

  # Orient
  ortmr=${regdir}/mr_bias_thr_ort.nii.gz

  if [[ "${noort}" == 0 ]]; then

    orientimg "${thrmr}" "${ort}" Cubic short "${ortmr}"

  else

    ortmr=${thrmr}

  fi

  # Crop to smallest roi
  mrroi=${regdir}/mr_bias_thr_roi.nii.gz
  croptosmall "${ortmr}" "${mrroi}"

  if [[ "${skull}" == 1 ]]; then

    # Change header * 10 dims
    hdmr=${regdir}/mr_bias_thr_ort_hd.nii.gz
    mulheader "${mrroi}" 10 "${hdmr}"

    # Skull strip
    betmr=${regdir}/mr_bias_thr_ort_bet.nii.gz
    skullstrip "${hdmr}" "${betmr}" "${frac}"

    # Update back header
    orghdmr=${regdir}/mr_bias_thr_ort_bet_orghd.nii.gz
    mulheader "${betmr}" "0.1" "${orghdmr}"

  else

    orghdmr=${mrroi}

  fi

  # Smooth
  # smmr=${regdir}/mr_bias_thr_ort_bet_sm.nii.gz
  # smoothimg ${orghdmr} 1 ${smmr}
  # smoothimg ${orghdmr} 0.25 ${smmr}

  # make MRI copy
  mrlnk=${regdir}/mr.nii.gz
  if [[ ! -f ${mrlnk} ]]; then cp "${orghdmr}" "${mrlnk}"; fi

  #---------------------------

  # 2a) initialize registration
  if [ "${atl}" == "allen" ]; then
    # Allen atlas template

    # FIX: Needs to addressed: same template for w/ or w/o bulb?

    # if [[ "${bulb}" == 0 ]]; then
    #     atlref=${atlasdir}/ara/template/average_template_50um_OBmasked.nii.gz

    # elif [[ "${bulb}" == 1 ]]; then
    atlref=${atlasdir}/ara/template/average_template_50um.nii.gz
    # fi
  elif [ "${atl}" == "dsurqe" ]; then

    atlref=${atlasdir}/dsurqe/template/DSURQE_40micron_average.nii.gz

  elif [ "${atl}" == "fischer" ]; then
    # Fischer atlas template
    atlref=${atlasdir}/fischer/template/Fischer344_template_stripped.nii.gz

  elif [ "${atl}" == "fischer" ]; then
    # Waxholm atlas template
    atlref=${atlasdir}/waxholm/template/WHS_SD_rat_T2star_v1.01.nii.gz

  else

    printf "ERROR: < -a => (atl) > only takes as inputs: allen, dsurge or fischer"
    exit 1

  fi
  #---------------------------

  # 2b) Register to Allen/Fischer atlas

  # Parameters:

  # # Out Allen
  # antsallen=${regdir}/allen_mr_antsWarped.nii.gz

  alad_xfm=${regdir}/mr_"${atl}"_affine.xfm
  alad_out=${regdir}/mr_"${atl}"_aladin.nii.gz

  # aladin
  ifdsntexistrun "${alad_xfm}" "Registering MRI data to ${atl^} atlas using affine reg" \
    reg_aladin -ref "${atlref}" -flo "${mrlnk}" -%i 95 -res "${alad_out}" -aff "${alad_xfm}" -maxit 15 -ln 4

  # reg_f3d
  cpp=${regdir}/mr_"${atl}"_cpp.nii.gz
  f3d_out=${regdirfinal}/mr_"${atl}"_f3d.nii.gz

  ifdsntexistrun "${f3d_out}" "Registering MRw data to ${atl^} atlas using deformable transformation"
  # reg_f3d -flo ${alad_out} -ref ${atlref} -res ${f3d_out} -cpp ${cpp} -sym -be 1e-3 -sx -15
  # reg_f3d -flo "${alad_out}" -ref "${atlref}" -res "${f3d_out}" -cpp "${cpp}" -be 1e-3 -sx -15
  set -x
  reg_f3d -flo "${alad_out}" -ref "${atlref}" -res "${f3d_out}" -cpp "${cpp}" -be "${be}" -sx "${sx}"
  set +x

  #---------------------------

  # 3) Warp Allen/Fischer labels to MRw

  base=$(basename "${lbls}")
  lblsname=${base%%.*}

  # Out lbls
  wrplbls=${regdirfinal}/${lblsname}_f3d.nii.gz

  # inv affine
  inv_aff=${regdir}/mr_"${atl}"_affine_inv.xfm

  ifdsntexistrun "${inv_aff}" "Inverting affine transform"
  # reg_transform -ref "${mrlnk}" -invAffine "${alad_xfm}" "${inv_aff}"
  reg_transform -ref "${atlref}" -invAffine "${alad_xfm}" "${inv_aff}"

  inv_cpp=${regdir}/mr_"${atl}"_cpp_backward.nii.gz

  ifdsntexistrun "${inv_cpp}" "Inverting control point grid"
  # reg_transform -ref "${mrlnk}" -invNrr "${cpp}" "${atlref}" "${inv_cpp}"
  # reg_transform -ref "${atlref}" -invNrr "${cpp}" "${atlref}" "${inv_cpp}"
  reg_transform -ref "${atlref}" -invNrr "${cpp}" "${alad_out}" "${inv_cpp}"

  # comb inv aff & def
  comb_def=${regdir}/"${atl}"_mr_comb_def.nii.gz

  ifdsntexistrun "${comb_def}" "Combing affine transform and deformable field"
  # reg_transform -ref ${inmr} -comp ${inv_aff} ${inv_cpp} ${comb_def}
  # reg_transform -ref "${mrlnk}" -comp "${inv_aff}" "${inv_cpp}" "${comb_def}"
  # reg_transform -ref "${inmr}" -comp "${inv_aff}" "${inv_cpp}" "${comb_def}"
  reg_transform -ref "${atlref}" -comp "${inv_aff}" "${inv_cpp}" "${comb_def}"

  # resample lbls
  ifdsntexistrun "${wrplbls}" "Resampling ${atl^} labels to MRI space"
  # reg_resample -ref "${mrlnk}" -flo "${lbls}" -trans "${comb_def}" -res "${wrplbls}" -inter 0
  reg_resample -ref "${inmr}" -flo "${lbls}" -trans "${comb_def}" -res "${wrplbls}" -inter 0

  #---------------------------

}

#--------------------

# call main function
main

# get script timing
END=$(date +%s)
DIFF=$((END - START))
DIFF=$((DIFF / 60))

miracl utils end_state -f "Registration and ${atl^} labels warping" -t "$DIFF minutes"

#--------------------

# create output file for successful completion
command="${vox}\n${ort}"
echo -e "$command" >>"reg_command.log"
