#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version_num.txt`
	printf "MIRACL pipeline v. $ver \n"
}


# help/usage function
function usage()
{
    
    cat <<usage

	1) Performs Structure Tensor Analysis (STA)

	Runs Matlab scripts
	
	Usage: `basename $0` 

	A GUI will open to choose your input down-sampled clarity nifti, brain mask, seed mask

		----------

	For command-line / scripting


	Usage: `basename $0` -i <down-sampled clarity nifti> -d <dog sigma> -g <gaussian sigma> -a <tracking angle threshold>
	                     -b <brain mask> -s <seed> -o <output dir>

	Example: `basename $0` -i clarity_03x_down_virus_chan.nii.gz -d 0.5 -g 0.5 -a 25 -b brain_mask.nii.gz -s seed.nii.gz -o sta

		required arguments:

			f. Input down-sampled clarity nifti (.nii/.nii.gz)

			d. Derivative of Gaussion (dog) sigma

			g. Gaussian smoothing sigma

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

    folderpath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f folder -s "$openstr")

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	folderpath=`cat path.txt`
	
	eval ${_inpath}="'$folderpath'"

#	rm path.txt

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

	while getopts ":i:b:a:s:d:g:o:" opt; do
    
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
            	angle=${OPTARG}
            	;;

            d)
            	dog=${OPTARG}
            	;;

            g)
            	gauss=${OPTARG}
            	;;

            o)
            	outdir=${OPTARG}
            	;;

        	*)
            	usage            	
            	;;

		esac
	
	done    	


	# check required input arguments

	if [ -z "${inclar}" ];
	then
		usage
		echo "ERROR: < -i => input clarity nifti> not specified"
		exit 1
	fi

	if [ -z "${angle}" ];
	then
		usage
		echo "ERROR: < -a => tracking angle> not specified"
		exit 1
	fi

    if [ -z "${dog}" ];
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

    if [ -z "${gauss}" ];
	then
		usage
		echo "ERROR: < -g => input gauss smoothing sigma> not specified"
		exit 1
	fi

else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

	printf "\n Reading input data \n"

	choose_file_gui "Open down-sampled clarity nifti" inclar
	
	# check required input arguments

	if [ -z "${inclar}" ];
	then
		usage
		echo "ERROR: <input down-sampled clarity nii> was not chosen"
		exit 1
	fi

	# options gui
	opts=$(${MIRACL_HOME}/sta/miracl_sta_gui.py -t "STA options" -f "dog sigma" "guass sigma" "angle"  -hf "`usage`")

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

	dog=`echo "${arr[3]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	printf "\n Chosen dog sigma: $dog \n"

	gauss=`echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen gaussian sigma: $gauss \n"

    angle=`echo "${arr[5]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

    printf "\n Chosen tracking angle: $angle \n"

fi


# get time

START=$(date +%s)

# run STA

if [ -z "${outdir}" ];
then
    outdir=clarity_sta
fi

# run matlab command
printf "\n Running Structure Tensor Analysis with the following command \n\n"

runMatlabCmd sta_track "'${inclar}'" "${dog}" "${gauss}" "${angle}" "'${brainmask}'" "'${seed}'" "'${outdir}'"

# get script timing 
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "Structure tensor analysis done in $DIFF minutes. Have a good day!"