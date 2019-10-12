CLARITY whole-brain registration to Allen atlas

The registration workflow relies on an autofluorescence channel input (tiff files),
and can perform whole-brain or hemisphere registrations to the Allen atlas

This workflow performs the following tasks:

    1) Sets orientation of input data using a GUI
    2) Converts TIFF to NII
	3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
	4) Warps Allen annotations to the original high-res CLARITY space
	5) Warps the higher-resolution CLARITY to Allen space (if chosen)

# Test data
A test dataset (CLARITY autofluorescence channel) for registration is found here under **data**:
https://stanfordmedicine.app.box.com/s/6kx5tfgbqd6ruk7uo0u64agn4oqpg39i

# GUI

Run

    miracl

and from the main GUI choose:

<img src="reg0.png" alt="alt text" width="450" height="500"/>

OR run:

    miracl_workflow_registration_clarity-allen_wb.sh

---


First choose the input tiff folder with the auto fluorescence channel:

<img src="../tiff_to_nii/tiff_to_nii2.png" alt="alt text" width="500" height="400"/>

this GUI will appear showing the data to orient it:

<img src="reg1.png" alt="alt text" width="550" height="500"/>

* you can navigate through the data using the bar bellow, by specifying the slice number
or using the arrows

<img src="reg2.png" alt="alt text" width="550" height="80"/>

* First choose the data plane (axial, coronal or sagittal)

<img src="reg3.png" alt="alt text" width="300" height="200"/>

* Then choose the orientation at the top and right of the image

<img src="reg4.png" alt="alt text" width="300" height="200"/>

* Then choose the orientation for scrolling through the slices (going into the page),
can confirm the orientation by changing the image number at the bottom (enter higher number and press Enter),
or using the Next or Prev image buttons

<img src="reg5.png" alt="alt text" width="300" height="200"/>

* Finally close the GUI

<img src="reg6.png" alt="alt text" width="350" height="150"/>

and the tiff conversion parameters:

<img src="reg7.png" alt="alt text" width="350" height="400"/>

Conversion parameters description:

    - out nii: Output nifti name
    - Down-sample ratio (default: 5)
    - Channel #: number for extracting single channel from multiple channel data (default: 1) [leave blank if single channel data/tiff files]
    - Chan prefix: string before channel number in file name [leave blank if single channel]
        for example if tiff file name has *_C001_*.tif for channel 1 and *_C002_*.tif for channel 2,
        to choose channel 1 if it's the auto fluorescence channel:-
        Chan number would be: 1
        Chan prefix would be: C00

    - channel name: output channel name (def= eyfp)
    - in-plane res: original resolution in x-y plane in um (default: 5)
    - z res: thickness (z-axis resolution / spacing between slices) in um (default: 5)
    - center: center of nifti file
and then choose the registration options:

<img src="reg8.png" alt="alt text" width="350" height="200"/>

Registration parameters description:

    - Hemi: warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
        accepted inputs are: <split> or <combined>  (default: combined)

    - Labels resolution: voxel size/Resolution of labels in um
        accepted inputs are: 10, 25 or 50  (default: 10)

    - olfactory bulb: if bulb is included in the dataset
        accepted inputs are: 0 -> not included (default), 1 -> included

    - side (only if registering hemisphere, else leave blank)
        accepted inputs are: rh (right hemisphere) or lh (left)


# Command-line

Usage:

miracl_workflow_registration_clarity-allen_wb.sh -f [Tiff folder]

Example:

miracl_workflow_registration_clarity-allen_wb.sh -f my_tifs -n "-d 5 -ch autofluo" -r "-o ARS -m combined -v 25"

arguments (required):

    f. Input Clarity tif dir/folder

optional arguments (remember the quotes):

    conversion to nii (invoked by -n " "):

    d.  [ Downsample ratio (default: 5) ]
    cn. [ chan # for extracting single channel from multiple channel data (default: 1) ]
    cp. [ chan prefix (string before channel number in file name). ex: C00 ]
    ch. [ output chan name (default: eyfp) ]
    vx. [ original resolution in x-y plane in um (default: 5) ]
    vz. [ original thickness (z-axis resolution / spacing between slices) in um (default: 5) ]
    c.  [ nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

    Registration (invoked by -r " "):

    o. Orient code (default: ALS)
    to orient nifti from original orientation to "standard/Allen" orientation

    m. Warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
    accepted inputs are: <split> or <combined>  (default: combined)

    v. Labels voxel size/Resolution of labels in um
        accepted inputs are: 10, 25 or 50  (default: 10)

    l. image of input Allen Labels to warp (default: annotation_hemi_split_10um.nii.gz - which are at a resolution of 0.01mm/10um)
        input could be at a different depth than default labels

        If l. is specified (m & v cannot be specified)


# Main Outputs

reg_final/clar_allen_space.nii.gz: Clarity data in Allen reference space

reg_final/clar_downsample_res(vox)um.nii.gz : Clarity data downsampled and oriented to "standard"

reg_final/annotation_hemi_(hemi)_(vox)um_clar_downsample.nii.gz : Allen labels registered to downsampled Clarity

reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif : Allen labels registered to oriented Clarity

reg_final/annotation_hemi_(hemi)_(vox)um_clar.tif: Allen labels registered to original (full-resolution) Clarity


# To visualize results

run

miracl_reg_check_results.py

Usage:

    miracl_reg_check_results.py -f [reg final folder] -v [visualization software] -s [reg space (clarity or
    allen)]

Example:

    miracl_convertTifftoNii.py -f reg_final -v itk -s clarity

Arguments (required):

    -f Input final registration folder

Optional arguments:

    -v Visualization software: itkSNAP 'itk' (default) or freeview 'free'
    -s Registration Space of results: clarity (default) or allen
