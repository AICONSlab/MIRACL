#!/usr/bin/env bash

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

    Workflow (wrapper) for structure tensor analysis (STA):

    1) Converts Tiff stack to nii (& down-sample)
    2) Uses registered labels to create seed mask & creates brain mask
	3) Run STA analysis
    #4) Computes viral signal per registered labels

    Executes:

        io/miracl_io_convertTifftoNII.py
        utils/miracl_extract_lbl.py
        utils/miracl_create_brainmask.py
        sta/miracl_sta_track_primary_eigen.py
        #lbls/miracl_lbls_stats.py


    Usage: `basename $0`

        A GUI will open to choose folder with tif files for STA and the registered Allen labels

        and choosing STA parameters
  
    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder] -o [output nifti] -l [Allen seed label] -r [Reg final dir] -d [ downsample ratio ]

    Example: `basename $0` -f my_tifs -o clarity_virus_05xdown.nii.gz -l PL -r clar_reg_final -n "-d 5 -ch autofluo" -t "-g 0.5 -k 0.5 -a 25"

        arguments (required):

            f. Input Clarity tif folder/dir [folder name without spaces]

            o. Output nifti

            l. Seed label abbreviation (from Allen atlas ontology)

            r. CLARITY final registration folder

        optional arguments (do not forget the quotes):

            d. Downsample ratio (default: 5)

            conversion (invoked by -n " "):                            

                    cn. [ chan # for extracting single channel from multiple channel data (default: 1) ]
                    cp. [ chan prefix (string before channel number in file name). ex: C00 ]
                    ch. [ output chan name (default: eyfp) ]
                    vx. [ original resolution in x-y plane in um (default: 5) ]
                    vz. [ original thickness (z-axis resolution / spacing between slices) in um (default: 5) ]
                    c.  [ nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

            sta parameters (invoked by -t " "):

                    g. [ Derivative of Gaussion (dog) sigma ]
			        k. [ Gaussian smoothing sigma ]
			        a. [ Tracking angle threshold ]
			    
	----------

	Main Outputs



    ----------

    Dependencies:

        - Matlab

        - Python 2.7

	-----------------------------------

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


#----------------------

# check dependencies

if [ -z ${MIRACL_HOME} ];
then

    printf "\n ERROR: MIRACL not initialized .. please run init/setup_miracl.sh  & rerun script \n"
	exit 1

fi


#----------------------

# get time

START=$(date +%s)


# output log file of script

exec > >(tee -i workflow_sta.log)
exec 2>&1

#---------------------------
#---------------------------

function choose_folder_gui()
{
	local openstrfol=$1
	local _inpathfol=$2

    folderpath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f folder -s "$openstrfol")

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	folderpath=`cat path.txt`

	eval ${_inpathfol}="'$folderpath'"

#	rm path.txt

}

function choose_file_gui()
{
	local openstrfil=$1
	local _inpathfil=$2

    filepath=$(${MIRACL_HOME}/io/miracl_io_file_folder_gui.py -f file -s "$openstrfil")

	filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	eval ${_inpathfil}="'$filepath'"

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

    printf "\n Reading input parameters \n"

	while getopts ":f:o:l:r:d:n:t:" opt; do

	    case "${opt}" in

            f)
            	indir="${OPTARG}"
            	;;

            o)
                nii="${OPTARG}"
                ;;

            l)
                lbl="${OPTARG}"
                ;;

            r)
                regdir="${OPTARG}"
                ;;

            d)
                down="${OPTARG}"
                ;;

            n)
            	convopts="${OPTARG}"
            	;;

            t)
            	staopts="${OPTARG}"
            	;;

        	*)
            	usage
            	;;

		esac

	done


	# check required input arguments

	if [ -z "${indir}" ];
	then
		usage
		echo "ERROR: < -f => input folder with clarity tifs> not specified"
		exit 1
	fi

    if [ -z "${nii}" ];
	then
		usage
		echo "ERROR: < -o => output nii> not specified"
		exit 1
	fi

	if [ -z "${lbl}" ];
	then
		usage
		echo "ERROR: < -l => input seed label> not specified"
		exit 1
	fi

    if [ -z "${regdir}" ];
	then
		usage
		echo "ERROR: < -r => input reg dir> not specified"
		exit 1
	fi

    if [ -z "${down}" ];
	then
		down=5
	fi

    #---------------------------
    # Call conversion to nii

    printf "\n Running conversion to nii with the following command: \n"

    printf "\n miracl_io_convertTifftoNII.py -f ${indir} ${convopts} -d ${down} -o ${nii} -dz 1 \n"
    miracl_io_convertTIFFtoNII.py -f ${indir} ${convopts} -d ${down} -o ${nii} -dz 1

    #---------------------------
    # Call extract lbl

    printf "\n Running label extraction with the following command: \n"

    reglbls=`echo ${regdir}/*_clar_downsample.nii.gz`

    printf "\n miracl_utils_extract_lbl.py -i ${reglbls} -l ${lbl} \n"
    miracl_utils_extract_lbl.py -i ${reglbls} -l ${lbl}

    #---------------------------
    # Call create brain mask

    printf "\n Running brain mask creation with the following command: \n"

    niifile=`echo niftis/${nii}*.nii.gz`

    printf "\n miracl_utils_create_brainmask.py -i ${niifile} \n"
    miracl_utils_create_brainmask.py -i ${niifile}

    #---------------------------
    # Call STA

    printf "\n Running STA with the following command: \n"

    printf "\n miracl_sta_track_primary_eigen.sh -i ${niifile} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz ${staopts} \n"
    miracl_sta_track_primary_eigen.sh -i ${niifile} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz ${staopts}

    #---------------------------
    # Call lbl stats

    #printf "\n Running signal statistics extraction with the following command: \n"

    #printf "\n miracl_lbls_stats.py -i ${niifile} -l ${reglbls} \n"
    #miracl_lbls_stats.py -i ${niifile} -l ${reglbls}

    #---------------------------
    #---------------------------


else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

    # Get options
#    choose_folder_gui "Open clarity dir (with .tif files) by double clicking then OK" indir

	# options gui
	opts=$(${MIRACL_HOME}/io/miracl_io_gui_options.py -t "STA workflow"  \
	        -d 'Input tiff folder' \
	        -f 'Out nii name (def = clarity)' 'Seed label abbreviation' 'CLARITY final registration folder' \
	           'Derivative of Gaussian (dog) sigma' 'Gaussian smoothing sigma' 'Tracking angle threshold' \
 	          'Downsample ratio (def = 5)'  'chan # (def = 1)' 'chan prefix' \
              'Out chan name (def = eyfp)' 'Resolution (x,y) (def = 5 "um")' 'Thickness (z) (def = 5 "um")' \
              'Downsample in z (def = 1)'  -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

	# check required input arguments

    indir=`echo "${arr[0]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	if [ -z "${indir}" ];
	then
		usage
		echo "ERROR: <input clarity directory> was not chosen"
		exit 1
	fi

	printf "\n Chosen in dir: $indir \n"

    nii=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen out nii name: $nii \n"

    lbl=`echo "${arr[2]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen seed label: $lbl \n"

    regdir=`echo "${arr[3]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen reg dir : $regdir \n"

    dog=`echo "${arr[4]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen Derivative of Gaussian : $dog \n"

    gauss=`echo "${arr[5]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen Gaussian smoothing sigma: $gauss \n"

    angle=`echo "${arr[6]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen tracking angle threshold: $angle \n"

    down=`echo "${arr[7]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen out nii name: $nii \n"

    chann=`echo "${arr[8]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen channel num: $chann \n"

    chanp=`echo "${arr[9]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen channel prefix: $chanp \n"

    chan=`echo "${arr[10]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen chan name: $chan \n"

    vx=`echo "${arr[11]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen vx: $vx \n"

    vz=`echo "${arr[12]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen vz: $vz \n"

    downz=`echo "${arr[13]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen down-samle in z: $downz \n"


    #---------------------------
    # Call conversion to nii

    printf "\n Running conversion to nii with the following command: \n"

    printf "\n miracl_io_convertTifftoNII.py -f ${indir} -d ${down} -o ${nii} -dz ${downz} \
            -chan ${chan} -chann ${chann} -chanp ${chanp} \n"
    miracl_io_convertTIFFtoNII.py -f ${indir} -d ${down} -o ${nii} -dz ${downz} \
                                    -chan ${chan} -chann ${chann} -chanp ${chanp}

    #---------------------------
    # Call extract lbl

    printf "\n Running label extraction with the following command: \n"

    reglbls=`echo ${regdir}/*_clar_downsample.nii.gz`

    printf "\n miracl_utils_extract_lbl.py -i ${reglbls} -l ${lbl} \n"
    miracl_utils_extract_lbl.py -i ${reglbls} -l ${lbl}

    #---------------------------
    # Call create brain mask

    printf "\n Running brain mask creation with the following command: \n"

    niifile=`echo niftis/${nii}*.nii.gz`

    printf "\n miracl_utils_create_brainmask.py -i ${niifile} \n"
    miracl_utils_create_brainmask.py -i ${niifile}

    #---------------------------
    # Call STA

    printf "\n Running STA with the following command: \n"

    printf "\n miracl_sta_track_primary_eigen.sh -i ${niifile} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz  \
               -dog ${dog} -gauss ${gauss} -angle ${angle} \n"
    miracl_sta_track_primary_eigen.sh -i ${niifile} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz ${staopts} \
                                     -dog ${dog} -gauss ${gauss} -angle ${angle}

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

echo "STA and signal analysis done in $DIFF minutes. Have a good day!"


# TODOs
# check registered labels space and res