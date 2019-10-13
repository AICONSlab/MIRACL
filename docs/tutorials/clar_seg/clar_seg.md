CLARITY whole-brain segmentation

There are multiple segmentation functions for different data (stains/channels):
*virus*, *cFos*, *sparse* and *nuclear*

The segmentation workflow relies on an output from the registration workflow,
but the segmentation wrapper function can be run without running the registration workflow

This workflow performs the following tasks:

    1) Segments neurons in cleared mouse brain of sparse or nuclear stains in 3D
    2) Voxelizes segmentation results into density maps with Allen atlas resolution
	3) Computes features of segmented image and summarizes them per label

executes:

    seg/miracl_seg_clarity_neurons_wrapper.sh
    seg/miracl_seg_voxelize_parallel.py
    seg/miracl_seg_feat_extract.py

# GUI

from the main GUI OR run:

    miracl_workflow_segmentation_clarity.sh

the following window will appear to choose input tiff folder with Thy1-YFP or other channel:

![input folder](seg1.png)

then choose the segmentation parameters:

![seg pars](seg2.png)

    - Channel type: virus, cFos, sparse (like Thy1 YFP) or nuclear (like PI)

    - Channel prefix & number if multiple channels (like Filter0001)

then choose the registered labels **annotation_hemi\__side_\_XXum_clar_vox.tif** to summarize segmentation features:

* where side -> combined or split, and
* XX is the resolution 10, 25 or 50

![reg labels](seg3.png)

# Command-line

Usage:

    miracl_workflow_segmentation_clarity.sh -f [Tiff folder]

Example:

    miracl_workflow_segmentation_clarity.sh -f my_tifs -t nuclear -s "-p C001" -e "-l reg_final/annotation_hemi_combined_25um_clar_vox.tif"

arguments (required):

    f. Input Clarity tif folder/dir [folder name without spaces]

    t. Channel type: sparse (like Thy1 YFP) or nuclear (like PI)

optional arguments (don't forget the quotes):

    Segmentation (invoked by -s " "):

        p. Channel prefix & number if multiple channels (like Filter0001)

    Feature extraction (invoked by -e " "):

        l. Allen labels (registered to clarity) used to summarize features

        reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif


# Main outputs


segmentation/seg.tif (.mhd) or seg_nuclear.tif (.mhd) : segmentation image with all labels (cells)
segmentation/seg_bin.tif (.mhd) or seg_bin_nuclear.tif (.mhd) : binarized segmentation image

voxelized_seg.(tif/nii)  (segmentation results voxelized to ARA resolution)
voxelized_seg_bin.(tif/nii) (binarized version)

clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA labels)

Results can be opened in Fiji for visualization