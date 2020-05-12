#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version.txt`
	printf "MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{
    
    cat <<usage

	1) Performs Structure Tensor Analysis (STA) on CLARITY viral tracing or stains

	Runs Matlab scripts
	
	Usage: `basename $0` 

	A GUI will open to choose your input down-sampled clarity nifti, brain mask, seed mask

		----------

	For command-line / scripting


	Usage: `basename $0` -i <down-sampled clarity nifti> -g <dog sigma> -k <gaussian sigma> -a <tracking angle threshold>
	                     -b <brain mask> -s <seed> -o <output dir>

	Example: `basename $0` -i clarity_03x_down_virus_chan.nii.gz -g 0.5 -k 0.5 -a 25 -b brain_mask.nii.gz -s seed.nii.gz -o sta

    OR using multiple parameters:

    `basename $0` -i clarity_03x_down_virus_chan.nii.gz -g 0.5,1.5 -k 0.5,2 -a 25,35 -b brain_mask.nii.gz -s seed.nii.gz -o sta


		required arguments:

			i. Input down-sampled clarity nifti (.nii/.nii.gz)

			g. Derivative of Gaussian (dog) sigma

			k. Gaussian smoothing sigma

			a. Tracking angle threshold

			b. Brain mask (.nii/.nii.gz)

			s. Seed mask (.nii/.nii.gz)

        optional arguments:

			o. Out dir


		----------

    Main Outputs

        fiber.trk => Fiber tracts

        ----------

	Dependencies:
	
		- Matlab

		- Diffusion Toolkit

	-----------------------------------

	(c) Qiyuan Tian @ Stanford University, 2016
	qytian@stanford.edu


    (c) Maged Goubran @ Stanford University, 2016
	mgoubran@stanford.edu

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

matdir=`which matlab`

if [[ -z "${matdir// }" ]];
then
	printf "\n ERROR: Matlab not initialized .. please install it & rerun script \n"
	exit 1
else 
	printf "\n Matlab path check: OK...\n"
fi

dtkdir=`which dti_tracker`

if [[ -z "${dtkdir// }" ]];
then
	printf "\n ERROR: Diffusion Toolkit not initialized .. please install it & rerun script \n"
	exit 1
else
	printf "\n Diffusion Toolkit path check: OK...\n"
fi

#------------


# GUI for CLARITY input imgs

function choose_file_gui()
{
	local openstr=$1
	local _inpath=$2

    folderpath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f folder -s "$openstr")

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	folderpath=`cat path.txt`
	
	eval ${_inpath}="'$folderpath'"

#	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:b:a:s:g:k:o:" opt; do
    
	    case "${opt}" in

	        i)
            	inclar="${OPTARG}"
            	;;

            b)
            	brainmask=${OPTARG}
            	;;

            s)
            	seed=${OPTARG}
            	;;

            a)
                set -f
                IFS=,
            	angles=($OPTARG)
            	;;

            g)
                set -f
                IFS=,
            	dogs=($OPTARG)
            	;;

            k)
                set -f
                IFS=,
            	gausses=($OPTARG)
            	;;

            o)
            	outdir=${OPTARG}
            	;;

        	*)
            	usage            	
            	;;

		esac
	
	done    	

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	#choose_file_gui "Open down-sampled clarity nifti" inclar
	
	# check required input arguments


	# options gui
	#opts=$(${MIRACL_HOME}/sta/miracl_sta_gui.py -t "STA options" -f "dog sigma" "guass sigma" "angle"  -hf "`usage`")
	opts=$(${MIRACL_HOME}/sta/sta_gui.py)

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

    inclar=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen CLARITY nii: $inclar \n"

    seed=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen Seed mask: $seed \n"

    brainmask=`echo "${arr[2]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen Brain mask: $brainmask \n"

	dogsin=`echo "${arr[3]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    dogs=($dogsin)

	printf "\n Chosen dog sigma: $dogs \n"

	gaussesin=`echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    gausses=($gaussesin)

    printf "\n Chosen gaussian sigma: $gausses \n"

    anglesin=`echo "${arr[5]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    angles=($anglesin)

    printf "\n Chosen tracking angle: $angles \n"


fi

# check required input arguments

if [ -z "${inclar}" ];
then
    usage
    echo "ERROR: < -i => input clarity nifti> not specified"
    exit 1
fi

if [ -z "${angles}" ];
then
    usage
    echo "ERROR: < -a => tracking angle> not specified"
    exit 1
fi

if [ -z "${dogs}" ];
then
    usage
    echo "ERROR: < -d => input dog sigma> not specified"
    exit 1
fi

if [ -z "${brainmask}" ];
then
    usage
    echo "ERROR: < -b => input brain mask> not specified"
    exit 1
fi

if [ -z "${seed}" ];
then
    usage
    echo "ERROR: < -s => input seed mask> not specified"
    exit 1
fi

if [ -z "${gausses}" ];
then
    usage
    echo "ERROR: < -g => input gauss smoothing sigma> not specified"
    exit 1
fi


# get time

START=$(date +%s)

# run STA

if [ -z "${outdir}" ];
then
    outdir=clarity_sta
fi

for angle in "${angles[@]}"; do

    for dog in "${dogs[@]}"; do

        for gauss in "${gausses[@]}"; do

            # run matlab command
            printf "\n Running Structure Tensor Analysis with the following command \n\n"

            "${MIRACL_HOME}"/utilfn/runMatlabCmd sta_track "'${curr_dir}/${inclar}'" "${dog}" "${gauss}" "${angle}" "'${curr_dir}/${brainmask}'" "'${curr_dir}/${seed}'" "'${curr_dir}/${outdir}'"

        done
    done
done

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Structure tensor analysis done in $DIFF minutes. Have a good day!"