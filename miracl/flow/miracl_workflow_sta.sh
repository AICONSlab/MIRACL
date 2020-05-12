#!/usr/bin/env bash

# get version
function getversion()
{
	ver=`cat ${MIRACL_HOME}/version.txt`
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

    Executes:
        conv/miracl_conv_convertTifftoNII.py
        lbls/miracl_lbls_get_graph_info.py
        lbls/miracl_lbls_generate_parents_at_depth.py
        utilfn/miracl_extract_lbl.py
        utilfn/miracl_create_brain_mask.py
        sta/miracl_sta_track_primary_eigen.py
        lbls/miracl_lbls_stats.py
        sta/miracl_sta_gen_tract_density.py

    Usage: `basename $0`

        A GUI will open to choose folder with tif files for STA and the registered Allen labels

        and choosing STA parameters
  
    ----------

	For command-line / scripting

    Usage: `basename $0` -f [Tiff folder] -o [output nifti] -l [Allen seed label] -m [ hemisphere ] -r [Reg final dir] -d [ downsample ratio ]

    Example: `basename $0` -f my_tifs -o clarity_virus -l PL -m combined -r clar_reg_final -d 5 -c AAV g 0.5 -k 0.5 -a 25

    Or for right PL:

    Example: `basename $0` -f my_tifs -o clarity_virus -l RPL -m split -r clar_reg_final -d 5 -c AAV -g 0.5 -k 0.5 -a 25

        arguments (required):
            f. Input Clarity tif folder/dir [folder name without spaces]
            o. Output nifti
            l. Seed label abbreviation (from Allen atlas ontology)
            r. CLARITY final registration folder
            m. Labels hemi
            g. [ Derivative of Gaussion (dog) sigma ]
            k. [ Gaussian smoothing sigma ]
            a. [ Tracking angle threshold ]

        optional arguments:
            d. Downsample ratio (default: 5)
            c. Output channel name
            n. chan # for extracting single channel from multiple channel data (default: 0)
            p. chan prefix (string before channel number in file name). ex: C00
            x. original resolution in x-y plane in um (default: 5)
            z. original thickness (z-axis resolution / spacing between slices) in um (default: 5)

	----------
	Main Outputs
        tract file = clarity_sta_[label]_seed/dog[dog]_gauss[gauss]/filter_ang[angle].trk
        virus stats csv = virus_signal_stats_depth_[depth].csv
        streamline density stats csv = sta_streamlines_density_stats_depth_[depth].csv
    ----------

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
if [ -z ${c3dpath} ];
then
    abspath_pwd="$( cd "$(dirname "$0")" ; pwd -P )"
    c3dpath="${abspath_pwd}/../../depends/c3d/bin"
    export PATH="$PATH:${abspath_pwd}/../../depends/c3d/bin"
fi

test_c3dpath=`which c3d`
if [ -z ${test_c3dpath} ];
then
    printf "\n ERROR: c3d not initialized .. please setup miracl & rerun script \n"
	exit 1
else
	printf "\n c3d path check: OK... \n"
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

    folderpath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f folder -s "$openstrfol")

	folderpath=`echo "${folderpath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

#	folderpath=`cat path.txt`

	eval ${_inpathfol}="'$folderpath'"

#	rm path.txt

}

function choose_file_gui()
{
	local openstrfil=$1
	local _inpathfil=$2

    filepath=$(${MIRACL_HOME}/conv/miracl_conv_file_folder_gui.py -f file -s "$openstrfil")

	filepath=`echo "${filepath}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`

	eval ${_inpathfil}="'$filepath'"

}


# Select Mode : GUI or script

if [[ "$#" -gt 1 ]]; then

	printf "\n Running in script mode \n"

    printf "\n Reading input parameters \n"

	while getopts ":f:o:l:r:d:n:m:g:k:a:c:n:p:x:z:" opt; do

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

            a)
            	angle="${OPTARG}"
            	;;

            g)
            	dog="${OPTARG}"
            	;;

            k)
            	gauss="${OPTARG}"
            	;;

            m)
            	hemi="${OPTARG}"
            	;;

            c)
            	chan="${OPTARG}"
            	;;

            n)
            	chann="${OPTARG}"
            	;;

            p)
            	chanp="${OPTARG}"
            	;;

            x)
            	vx="${OPTARG}"
            	;;

            z)
            	vz="${OPTARG}"
            	;;

        	*)
            	usage
            	;;

		esac

	done


	# check required input arguments

	if [[ -z "${indir}" ]];
	then
		usage
		echo "ERROR: < -f => input folder with clarity tifs> not specified"
		exit 1
	fi

    if [[ -z "${nii}" ]];
	then
		usage
		echo "ERROR: < -o => output nii> not specified"
		exit 1
	fi

	if [[ -z "${lbl}" ]];
	then
		usage
		echo "ERROR: < -l => input seed label> not specified"
		exit 1
	fi

    if [[ -z "${regdir}" ]];
	then
		usage
		echo "ERROR: < -r => input reg dir> not specified"
		exit 1
	fi

    if [[ -z "${down}" ]];
	then
		down=5
	fi

    if [[ -z "${hemi}" ]];
	then
		hemi="combined"
	fi

    if [[ -z "${chan}" ]];
	then
		chan="virus"
	fi

    if [[ -z "${chann}" ]];
	then
		chann=0
	fi

    if [[ -z "${chanp}" ]];
	then
		chanp=""
	fi

    if [[ -z "${vx}" ]];
	then
		vx=5
	fi

    if [[ -z "${vz}" ]];
	then
		vz=5
	fi


    #---------------------------
    # Call conversion to nii

    down=`printf %02d ${down}`

    nii_file=niftis/${nii}_${down}x_down_${chan}_chan.nii.gz

    if [[ ! -f ${nii_file} ]]; then

        printf "\n Running conversion to nii with the following command: \n"

        printf "\n miracl conv tiff_nii -f ${indir} -cn ${chann} -cp ${chanp} -ch ${chan} -vx ${vx} -vz ${vz} \
         -d ${down} -o ${nii} -dz 1 \n"
        miracl conv tiff_nii -f ${indir} -cn ${chann} -cp ${chanp} -ch ${chan} -vx ${vx} -vz ${vz} \
         -d ${down} -o ${nii_file} -dz 1

    else

        printf "\n Nifti file already created for this channel\n"

    fi

    #---------------------------
    # Call extract lbl

    reg_lbls=${regdir}/annotation_hemi_${hemi}_??um_clar_space_downsample.nii.gz
    #reg_lbls=`echo ${regdir}/annotation_hemi_${hemi}_??um_clar_space_downsample.nii.gz`

    if [[ "${hemi}" == "combined" ]]; then

        # get chosen depth
        depth=`miracl lbls graph_info -l ${lbl} | grep depth | tr -dc '0-9'`

    else

        clbl=${lbl:1:${#lbl}}
        depth=`miracl lbls graph_info -l ${clbl} | grep depth | tr -dc '0-9'`

    fi

    deep_lbls=`echo annotation_hemi_${hemi}_??um_clar_space_downsample_depth_${depth}.nii.gz`
    #deep_lbls=`echo *_depth_${depth}.nii.gz`
    #free_lbls=annotation_hemi_${hemi}_clar_space_downsample_depth_${depth}_freeview.nii.gz

    if [[ ! -f ${deep_lbls} ]]; then

        printf "\n Generating grand parent labels for ${lbl} at depth ${depth} \n"

        miracl lbls parents_at_depth -l ${reg_lbls} -d ${depth}

        c3d ${reg_lbls} ${deep_lbls} -copy-transform -o ${deep_lbls}

    else

        printf "\n Grand parent labels already created at this depth \n"

    fi

    lbl_mask=${lbl}_mask.nii.gz

    if [[ ! -f ${lbl_mask} ]]; then

        printf "\n Running label extraction with the following command: \n"

        printf "\n miracl utilfn extract_lbl -i ${deep_lbls} -l ${lbl} -m ${hemi} \n"
        miracl utilfn extract_lbl -i ${deep_lbls} -l ${lbl} -m ${hemi}

    else

        printf "\n Label mask already created \n"

    fi

    #---------------------------
    # Call create brain mask

    brain_mask=clarity_brain_mask.nii.gz

    if [[ ! -f ${brain_mask} ]]; then

        printf "\n Running brain mask creation with the following command: \n"

        printf "\n miracl utilfn brain_mask -i ${nii_file} \n"
        miracl utilfn brain_mask -i ${nii_file}

    else

        printf "\n Brain mask already created \n"

    fi

    #---------------------------
    # Call STA

    out_dir=clarity_sta_${lbl}_seed

    sta_dir=${out_dir}/dog${dog}gau${gauss}

    if [[ ! -d ${sta_dir} ]]; then

        printf "\n Running STA with the following command: \n"

        printf "\n miracl sta primary_eigen -i ${nii_file} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz \
        -o ${out_dir} -g ${dog} -k ${gauss} -a ${angle} \n"
        miracl sta primary_eigen -i ${nii_file} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz -o ${out_dir} \
        -g ${dog} -k ${gauss} -a ${angle}

    else

        printf "\n STA already run with the specified parameters \n "

    fi

    #---------------------------

    lbl_stats=virus_signal_stats_depth_${depth}.csv

    if [[ ! -f ${lbl_stats} ]]; then

        printf "\n Computing signal statistics with the following command: \n"

        printf "\n miracl lbls stats -i ${nii_file} -l ${deep_lbls} -o ${lbl_stats} -m ${hemi} -d ${depth} -s Max \n"
        miracl lbls stats -i ${nii_file} -l ${deep_lbls} -o ${lbl_stats} -m ${hemi} -d ${depth} -s Max

    else

        printf "\n Signal statistics already computed at this depth \n"

    fi

    #---------------------------

    # gen tract density map
    tracts=${sta_dir}/fiber_ang${angle}.trk
    dens_map=${sta_dir}/sta_streamlines_density_map.nii.gz
    dens_map_clar=${sta_dir}/sta_streamlines_density_map_clar_space.nii.gz
    ga_vol=${sta_dir}/ga.nii.gz

    if [[ ! -f ${dens_map_clar} ]]; then

        printf "\n Generating tract density map with the following command: \n"

        printf "\n miracl sta tract_density.py -t ${tracts} -r ${ga_vol} -o ${dens_map} \n"
        miracl sta tract_density.py -t ${tracts} -r ${ga_vol} -o ${dens_map}

        echo c3d ${nii_file} ${dens_map} -copy-transform ${dens_map_clar}
        c3d ${nii_file} ${dens_map} -copy-transform ${dens_map_clar}

    else

        printf "\n Tract density map already generated \n "

    fi

    #---------------------------

    # gen label stats for density
    dens_stats=${sta_dir}/sta_streamlines_density_stats_depth_${depth}.csv

    if [[ ! -f ${dens_stats} ]]; then

        printf "\n Computing tract density statistics with the following command: \n"

        printf "\n miracl lbls stats.py -i ${dens_map_clar} -l ${deep_lbls} -o ${dens_stats} -m ${hemi} -d ${depth} \n"
        miracl lbls stats.py -i ${dens_map_clar} -l ${deep_lbls} -o ${dens_stats} -m ${hemi} -d ${depth}

    else

        printf "\n Tract density statistics already computed at this depth \n"

    fi

    # gen force graph for signal stats
#    signal_graph=virus_signal_connectivity_graph_depth_${depth}.html
#
#    if [[ ! -f ${signal_graph} ]]; then
#
#        printf " \n Generating virus signal connectivity graph with the following command: \n "
#
#        printf "\n miracl_sta_create_force_graph.py -l ${lbl_stats} -m ${hemi} -o ${signal_graph} \n "
#        miracl_sta_create_force_graph.py -l ${lbl_stats} -m ${hemi} -o ${signal_graph}
#
#    else
#
#        printf "\n Virus signal connectivity graph already computed at this depth \n"
#
#    fi
#
#    # gen force graph for tract density
#    tract_graph=sta_streamlines_density_connectivity_graph_depth_${depth}.html
#
#    if [[ ! -f ${tract_graph} ]]; then
#
#        printf " \n Generating virus signal connectivity graph with the following command: \n "
#
#        printf "\n miracl_sta_create_force_graph.py -l ${dens_stats} -m ${hemi} -o ${tract_graph} \n "
#        miracl_sta_create_force_graph.py -l ${dens_stats} -m ${hemi} -o ${tract_graph}
#
#    else
#
#        printf "\n Tract density connectivity graph already computed at this depth \n"
#
#    fi

    #---------------------------
    #---------------------------


else

	# call gui

	printf "\n No inputs given ... running in GUI mode \n"

    # Get options
#    choose_folder_gui "Open clarity dir (with .tif files) by double clicking then OK" indir

	# options gui
	opts=$(${MIRACL_HOME}/conv/miracl_conv_gui_options.py -t "STA workflow"  \
	        -d "Input tiff folder" "CLARITY final registration folder" \
	        -f "Out nii name (def = clarity)" "Seed label abbreviation" "hemi (combined or split)" \
	           "Derivative of Gaussian (dog) sigma" "Gaussian smoothing sigma" "Tracking angle threshold" \
 	          "Downsample ratio (def = 5)"  "chan # (def = 1)" "chan prefix" \
              "Out chan name (def = AAV)" "Resolution (x,y) (def = 5 um)" "Thickness (z) (def = 5 um)" \
              "Downsample in z (def = 1)"  -hf "`usage`")

	# populate array
	arr=()
	while read -r line; do
	   arr+=("$line")
	done <<< "$opts"

	# check required input arguments

    indir="$(echo -e "${arr[0]}" | cut -d ':' -f 2 | tr -d '[:space:]')"

	if [[ -z "${indir}" ]];
	then
		usage
		echo "ERROR: <input clarity directory> was not chosen"
		exit 1
	fi

	printf "\n Chosen in dir: $indir \n"

    regdir="$(echo -e "${arr[1]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    # regdir=`echo "${arr[1]}" | cut -d ':' -f 2 | sed -e 's/^ "//' -e 's/"$//'`
    printf "\n Chosen reg dir: $regdir \n"

    nii="$(echo -e "${arr[2]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${nii}" ]]; then nii='clarity'; fi
    printf "\n Chosen out nii name: $nii \n"

    lbl="$(echo -e "${arr[3]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    printf "\n Chosen seed label: $lbl \n"

    hemi="$(echo -e "${arr[4]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    printf "\n Chosen label hemi: $hemi \n"

    dog="$(echo -e "${arr[5]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${dog}" ]]; then dog="0.5,1.5"; fi
    printf "\n Chosen Derivative of Gaussian : $dog \n"

    gauss="$(echo -e "${arr[6]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${gauss}" ]]; then gauss="0.5,2"; fi
    printf "\n Chosen Gaussian smoothing sigma: $gauss \n"

    angle="$(echo -e "${arr[7]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${angle}" ]]; then angle="25,35"; fi
    printf "\n Chosen tracking angle threshold: $angle \n"

    down="$(echo -e "${arr[8]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${down}" ]]; then down=5; fi
    down=$( printf "%02d" $down ) # add leading zeros
    printf "\n Chosen downsample ratio: $down \n"
    
    chann="$(echo -e "${arr[9]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${chann}" ]]; then chann=""; fi
    printf "\n Chosen channel num: $chann \n"

    chanp="$(echo -e "${arr[10]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${chanp}" ]]; then chanp=""; fi
    printf "\n Chosen channel prefix: $chanp \n"

    chan="$(echo -e "${arr[11]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${chan}" ]]; then chan="AAV"; fi
    printf "\n Chosen chan name: $chan \n"

    vx="$(echo -e "${arr[12]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${vx}" ]]; then vx=5; fi
    printf "\n Chosen vx: $vx \n"

    vz="$(echo -e "${arr[13]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${vz}" ]]; then vz=5; fi
    printf "\n Chosen vz: $vz \n"

    downz="$(echo -e "${arr[14]}" | cut -d ':' -f 2 | tr -d '[:space:]')"
    if [[ -z "${downz}" ]]; then downz=1; fi
    printf "\n Chosen down-sample in z: $downz \n"


    #---------------------------
    # Call conversion to nii

    nii_file=niftis/${nii}_${down}x_down_${chan}_chan.nii.gz

    if [[ ! -f ${nii_file} ]]; then

        printf "\n Running conversion to nii with the following command: \n"

        if [[ -n ${chanp} ]]; then
            printf "\n miracl conv tiff_nii -f ${indir} -d ${down} -o ${nii} -dz ${downz} -ch ${chan} -cn ${chann} -cp ${chanp} \n"
            miracl conv tiff_nii -f ${indir} -d ${down} -o ${nii} -dz ${downz} \
                                            -ch ${chan} -cn ${chann} -cp ${chanp}
        else
            printf "\n miracl conv tiff_nii -f ${indir} -d ${down} -o ${nii} -dz ${downz} -ch ${chan}\n"
            miracl conv tiff_nii -f ${indir} -d ${down} -o ${nii} -dz ${downz} -ch ${chan}
        fi

    else

        printf "\n Nifti file already created for this channel\n"

    fi

    #---------------------------
    # Call extract lbl

    reg_lbls=${regdir}/annotation_hemi_${hemi}_??um_clar_space_downsample.nii.gz

    if [[ "${hemi}" == "combined" ]]; then
        # get chosen depth
        depth=`miracl lbls graph_info -l ${lbl} | grep depth | tr -dc '0-9'`

    else

        clbl=${lbl:1:${#lbl}}
        echo $clbl
        echo "miracl lbls graph_info -l ${clbl} | grep depth | tr -dc '0-9'"
        depth=`miracl lbls graph_info -l ${clbl} | grep depth | tr -dc '0-9'`

    fi

    deep_lbls=annotation_hemi_${hemi}_??um_clar_space_downsample_depth_${depth}.nii.gz
    #free_lbls=annotation_hemi_${hemi}_clar_space_downsample_depth_${depth}_freeview.nii.gz

    if [[ ! -f ${deep_lbls} ]]; then

        printf "\n Generating grand parent labels for ${lbl} at depth ${depth} \n"

        miracl lbls gp_at_depth -l ${reg_lbls} -d ${depth}

        c3d ${reg_lbls} ${deep_lbls} -copy-transform -o ${deep_lbls}

    else

        printf "\n Grand parent labels already created at this depth \n"

    fi

    lbl_mask=${lbl}_mask.nii.gz

    if [[ ! -f ${lbl_mask} ]]; then

        printf "\n Running label extraction with the following command: \n"

        printf "\n miracl utils extract_lbl -i ${deep_lbls} -l ${lbl} -m ${hemi} \n"
        miracl utils extract_lbl -i ${deep_lbls} -l ${lbl} -m ${hemi}

    else

        printf "\n Label mask already created \n"

    fi

    #---------------------------
    # Call create brain mask

    brain_mask=clarity_brain_mask.nii.gz

    if [[ ! -f ${brain_mask} ]]; then

        printf "\n Running brain mask creation with the following command: \n"

        printf "\n miracl utilfn brain_mask -i ${nii_file} \n"
        miracl utils brain_mask -i ${nii_file}

    else

        printf "\n Brain mask already created \n"

    fi

    #---------------------------
    # Call STA

    out_dir=clarity_sta_${lbl}_seed

    printf "\n Running STA with the following command: \n"

    printf "\n miracl sta track_tensor -i ${nii_file} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz  \
               -dog ${dog} -gauss ${gauss} -angle ${angle} -o ${out_dir} \n"
    miracl sta track_tensor -i ${nii_file} -b clarity_brain_mask.nii.gz -s ${lbl}_mask.nii.gz \
                                     -g ${dog} -k ${gauss} -a ${angle} -o ${out_dir}

    #---------------------------
    # Call lbl stats

    lbl_stats=virus_signal_stats_depth_${depth}.csv

    if [[ ! -f ${lbl_stats} ]]; then

        printf "\n Computing signal statistics with the following command: \n"

        printf "\n miracl lbls stats -i ${nii_file} -l ${deep_lbls} -o ${lbl_stats} -m ${hemi} -d ${depth} -s Max \n"
        miracl lbls stats -i ${nii_file} -l ${deep_lbls} -o ${lbl_stats} -m ${hemi} -d ${depth} -s Max

    else

        printf "\n Signal statistics already computed at this depth \n"

    fi

    #---------------------------

    # gen tract density map

    # loop over all derivative of gaussian and gaussian smoothing values
    for dog_sigma in ${dog//,/ }; do

        for gauss_sigma in ${gauss//,/ }; do

            for angle_val in ${angle//,/ }; do
                sta_dir=${out_dir}/dog${dog_sigma}gau${gauss_sigma}
                tracts=${sta_dir}/fiber_ang${angle_val}.trk
                dens_map=${sta_dir}/sta_streamlines_density_map.nii.gz
                dens_map_clar=${sta_dir}/sta_streamlines_density_map_clar_space_angle_${angle_val}.nii.gz
                ga_vol=${sta_dir}/ga.nii.gz

                if [[ ! -f ${dens_map_clar} ]]; then

                    printf "\n Generating tract density map with the following command: \n"

                    printf "\n miracl sta tract_density -t ${tracts} -r ${ga_vol} -o ${dens_map} \n"
                    miracl sta tract_density -t ${tracts} -r ${ga_vol} -o ${dens_map}

                    echo c3d ${nii_file} ${dens_map} -copy-transform ${dens_map_clar}
                    c3d ${nii_file} ${dens_map} -copy-transform ${dens_map_clar}

                else

                    printf "\n Tract density map already generated \n "

                fi

                # gen label stats for density
                dens_stats=${sta_dir}/sta_streamlines_density_stats_depth_${depth}_angle_${angle_val}.csv

                if [[ ! -f ${dens_stats} ]]; then

                    printf "\n Computing tract density statistics with the following command: \n"

                    printf "\n miracl lbls stats -i ${dens_map_clar} -l ${deep_lbls} -o ${dens_stats} -m ${hemi} -d ${depth} \n"
                    miracl lbls stats -i ${dens_map_clar} -l ${deep_lbls} -o ${dens_stats} -m ${hemi} -d ${depth}

                else

                    printf "\n Tract density statistics already computed at this depth \n"

                fi


            done
        done
    done

fi


#---------------------------
#---------------------------


# get script timing
END=$(date +%s)
DIFF=$((END-START))
DIFF=$((DIFF/60))

miracl utils end_state -f "STA and signal analysis " -t "$DIFF minutes"

# TODOs
# streamline after reg
# add assert if nii and lbls are same size
# check registered labels space and res