#!/bin/bash

# help/usage function
function help()
{
    
    cat <<help

   	CLARITY project / Mouse / Stroke study 

	1) Segments neurons in clear mouse brain in 3D

	Runs a Fiji/ImageJ macro based on the 3D plugin (3D Fast Filters, 3D Spot Segmentations)
	
	Usage: `basename $0` <group (stroke or control)> <<mouse #> 

	Example: `basename $0` stroke 17 

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2016
	mgoubran@stanford.edu
	
	-----------------------------------

help

	exit 1

}

# Call help/usage function
if [[ $# -lt 2 || "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then
    help >&2
fi

grp=$1
id=$2

projectdir=/data/clarity_project/mouse/stroke_study

datadir=$projectdir/${grp}
subjdir=$datadir/${id}

#macro=/data/clarity_project/scripts/seg/whole_brain_clarity_mouse_neurons_seg_3D.ijm
macro=/data/clarity_project/scripts/seg/miracl_seg_neurons_3D_wb_clarity_cortical.ijm
segdir=$subjdir/seg
clardir=$subjdir/CLARITY
tifdir=$clardir/tifs
# fijidir=$clardir/segmentation

# make seg dir
if [[ ! -d $segdir || ! -d $fijidir ]];then

	printf "\n Creating Segmentation folder\n"
	mkdir -p $segdir #$fijidir

fi

# split filters

if [[ ! -d $tifdir/filter0 ]]; then
	
	mkdir $tifdir/filter0 $tifdir/filter1
	mv $tifdir/*Filter0000* $tifdir/filter0/.
	mv $tifdir/*Filter0001* $tifdir/filter1/.

fi


# free up cached memory -- needs sudo permissions
printf "\n Freeing up cached memory \n"

echo "sync; echo 3 | sudo tee /proc/sys/vm/drop_caches"
#sync; echo 3 | sudo tee /proc/sys/vm/drop_caches 1>/dev/null


# Loop over stacks for memory efficiency

# stack size in tifs < 2 GB
szstk=125;
ntifs=`ls $tifdir/filter0/*.tif | wc -l`

nstk=`printf "%.0f" $(echo "scale=2;$ntifs/$szstk" | bc)`
# nstk=$(($nstk+1))

for i in `seq 1 $nstk`; do
	
	stackdir=$tifdir/filter0/stack_${i}
	mkdir -p $stackdir

	echo "processing stack $i"

	if [[ $i == 1 ]]; then
			
			aslice=`printf "%04d" 0`;
			zslice=`printf "%04d" $(echo $szstk)`;

		else

			aslice=`printf "%04d" $(echo "($szstk*($i-1))+1" | bc)`;
			zslice=`printf "%04d" $(echo "($szstk*$i)" | bc)`;

	fi

	# move files 	
	if [ "$(ls -A $stackdir)" ]; then 

		echo "slices for stack $i already moved"

	else		

		echo "moving slices $aslice to $zslice into stack dir"	

		for s in `seq ${aslice} ${zslice}`; do

			s=`printf "%04d" $s`;

			# echo ${s}

			mv ${tifdir}/filter0/*${s}.ome.tif ${stackdir}/. 2>/dev/null

		done

	fi

	path=$stackdir

	outseg=$stackdir/seg.mhd
	log=$segdir/Fiji_seg_log_stack_${i}.txt 

	if [[ ! -f $outseg ]]; then

		printf "\n Performing Segmentation using Fiji \n"
		
		echo Fiji -macro $macro "${path}" | tee $log 
		Fiji -macro $macro "${path}/" | tee $log

		outnii=$segdir/segmentation_lbl_s${i}.nii.gz

		# convert to nii
		printf "\n Converting TIF output to Nii \n"
		c3d $outseg -o $outnii -type short

		# # adjust header
		# v=`mri_head -read $outnii | grep xsize | cut -d ' ' -f 4`
		# mri_modify -zsize $v $outnii $outnii

		sleep 5

	else

		echo "Segmentation already computed for stack $i.. processing next stack"

	fi

done

# move tifs back
mv $tifdir/filter0/stack_?/*Filter*.tif $tifdir/filter0/.  2>/dev/null
mv $tifdir/filter0/stack_??/*Filter*.tif $tifdir/filter0/. 2>/dev/null

combseg=$segdir/comb_seg_lbl.nii.gz

# echo c3d $segdir/segmentation_lbl_s* -tile z -o $combseg -type short
# c3d $segdir/segmentation_lbl_s* -tile z -o $combseg -type short

echo "Segmentation done. Have a good day!"
