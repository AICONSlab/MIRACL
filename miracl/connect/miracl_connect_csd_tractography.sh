#!/bin/bash

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

    Performs CSD tractography and track density mapping for a seed region using MRtrix3
    
    1) Computes response function of the diffusion data
    2) Computes fiber orientation distribution (FOD) from the response function
    3) Performs probabilistic CSD tractography using the iFOD2 method
    4) Computes a tract density image (# of tracks / voxel)
    5) Converts tracts to vtk format (for visualization in other software like 3DSlicer,Paraview..) 

    Usage: `basename $0` -d <DTI data> -m <binary mask> -r <bvecs> -b <bvals> -s <seed> -v <vox> -t <output tract name> -f <DTI dir> -e <exclusion seed> -p tckgen (tracking) options 

    Example: `basename $0` -d dti.nii.gz -m dti_mask.nii.gz -r dti.bvecs -b dti.bvals -s seed.nii.gz -v 1 -t CST -f dti_folder -e dti_exlcude_seed.nii.gz -p "-cutoff 0.2 -number 2000"


Required arguments:

    d. DTI data

    m. DTI mask

    r. DTI bvecs

    b. DTI bvals 

    s. Tractography seed

    v. Tract density map voxel size (in mm)

    t. Output tract name

    f. Directory containing DTI data

Optional arguments:

	e. Exclusion seed for editing tracts

	p. Tckgen (tractography) options 

	
    ----------

	Dependencies:

	- MRtrix3
	http://www.mrtrix.org

	-----------------------------------

	(c) Maged Goubran @ AICONSlab, 2022
	maged.goubran@utoronto.ca
	
	-----------------------------------
	
usage

}

# Call help/usage function

if [[ "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then
    
    usage >&2
    exit 1

fi

# get arguments

while getopts ":d:m:r:b:s:v:t:f:e:p:" opt; do
    
    case "${opt}" in
       
        d)
            dti=${OPTARG}
            ;;
        m)
            mask=${OPTARG}
            ;;
        r)
            bvec=${OPTARG}
            ;;
        b)
            bval=${OPTARG}
            ;;       
        s)
            seed=${OPTARG}
            ;;
        v)
            vox=${OPTARG}
            ;;
        t)
            track=${OPTARG}
            ;;
        f)
            workdir=${OPTARG}
            ;;
        e)
            excludeseed=${OPTARG}
            ;;
        p)
        	set -f
        	IFS=' '
        	trackpars="${OPTARG}"
        	;;   
        *)
            usage
            ;;
    
    esac

done

#----------

# check dependencies

if [ -z ${MIRACL_HOME} ];
then

    printf "\n ERROR: MIRACL not initialized .. please run init/setup_miracl.sh & rerun script \n"
	exit 1

fi

mrtrixpath=`which tckgen`

if [ -z ${mrtrixpath} ];
then
	printf "\n ERROR: MRtrix3 not initialized .. please install it & rerun script \n"
	exit 1
else 
	printf "\n MRtrix3 path check: OK... \n" 
fi

#----------

# check required input arguments

if [ -z ${dti} ];
then
	usage
	echo "ERROR: < -d => dti data> not specified"
	exit 1
fi


if [ -z ${mask} ];
then
	usage
	echo "ERROR: < -m => mask> not specified"
	exit 1
fi

if [ -z ${bvec} ];
then
	usage
	echo "ERROR: < -r => bvecs> not specified"
	exit 1
fi

if [ -z ${bval} ];
then
	usage
	echo "ERROR: < -b => bvals> not specified"
	exit 1
fi

if [ -z ${seed} ];
then
	usage
	echo "ERROR: < -s => seed> not specified"
	exit 1
fi

if [ -z ${vox} ];
then
	usage
	echo "ERROR: < -v => voxel size> not specified"
	exit 1
fi

if [ -z ${track} ];
then
	usage
	echo "ERROR: < -t => Output tract name> not specified"
	exit 1
fi

if [ -z ${workdir} ];
then
	usage
	echo "ERROR: < -f => DTI directory> not specified"
	exit 1
fi


# generate log file

exec > >(tee -i ${workdir}/mrtrix_csd_tdi_script.log)
exec 2>&1


pushd $workdir

#---------------------------------

# 1. Compute response function

response=response.txt

if [[ ! -f $response ]]; then

	printf "\n Computing response function\n"
	
	echo dwi2response tournier $dti $response -mask $mask -fslgrad $bvec $bval 
	dwi2response tournier $dti $response -mask $mask -fslgrad $bvec $bval > >(tee response.err) 2> >(tee response.out >&2)
	
else

	printf "\n Response function already computed .. skipping\n"

fi

#---------------------------------

# 2. Compute ODF from response 

fod=dti_fod.nii.gz

if [[ ! -f $fod ]]; then
	
	printf "\n Computing ODF from response function\n"

	echo dwi2fod $dti $response $fod -mask $mask -fslgrad $bvec $bval 
	dwi2fod $dti $response $fod -mask $mask -fslgrad $bvec $bval > >(tee fod.err) 2> >(tee fod.out >&2)

else

	printf "\n ODF already computed .. skipping\n"

fi  

#---------------------------------

# 3. CSD tractography

trackdir=tracks

if [[ ! -d $trackdir ]]; then
	
	echo mkdir -p $trackdir
	mkdir -p $trackdir

fi

tracks=${trackdir}/${track}.tck

echo trackpars: "$trackpars"

if [[ ! -f $tracks ]]; then
	
	printf "\n Generating tractography of ${track} while seeding from ${seed}\n"

	echo tckgen $fod $tracks -seed_image $seed "$trackpars" 
	tckgen $fod $tracks -seed_image $seed `echo "$trackpars"` > >(tee tckgen.err) 2> >(tee tckgen.out >&2)

else

	printf "\n Tractography already done .. skipping\n"	

fi

#---------------------------------

# 4. Edit tracks - if needed 

if [ ! -z ${excludeseed} ];
then

	edittracks=${trackdir}/${track}_edited.tck

	if [[ ! -f $edittracks ]]; then

		printf "\n Editing ${track} by excluding tracts passing through ${excludeseed}\n"

		echo tckedit $tracks -exclude $excludeseed $edittracks
		tckedit $tracks -exclude $excludeseed $edittracks

	else

		printf "\n Editing already done .. skipping\n"

	fi

fi

#---------------------------------

# 5. Generate track density map  

tracksmap=${trackdir}/${track}_map.nii.gz

if [[ ! -f $tracksmap ]]; then
	
	if [[ -f $edittracks ]]; then
		
		tracks=$edittracks

	fi

	printf "\n Generating tract density map of ${track} on a grid with a voxel size of ${vox}\n"

	echo tckmap $tracks $tracksmap -vox $vox -dec
	tckmap $tracks $tracksmap -vox $vox -dec

else

	printf "\n TDI already done ...\n"

fi

#---------------------------------

# 6. Convert tracks to vtk  

vtktracks=${trackdir}/${track}.vtk

if [[ ! -f ${vtktracks} ]]; then
	
	printf "\n Converting tracks to vtk format ...\n"

	echo tckconvert ${tracks} ${vtktracks}
	tckconvert ${tracks} ${vtktracks}

else

	printf "\n Track conversion already done ...\n"

fi

popd

printf "\n Tractography & Tract density mapping done .. Have a good day!\n"
