MRI whole-brain registration to Allen atlas

This workflow performs the following tasks:

	1) Registers in-vivo or ex-vivo MRI data to Allen Reference mouse brain Atlas
	2) Warps Allen annotations to the MRI space

# GUI

from the main GUI OR run:

    miracl reg mri_allen_nifty

this window will open to choose the input MRI nii (preferable T2-w):

![](reg_options.png)

then choose registration options:

    -  orient code (default: RSP)
        to orient nifti from original orientation to "standard/Allen" orientation

    -  hemisphere mirror (default: combined)
        warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
        accepted inputs are: <split> or <combined>

    -  labels voxel size/Resolution in um (default: 10)
        accepted inputs are: 10, 25 or 50

    -  olfactory bulb included in brain, binary option (default: 0 -> not included)

    -  skull strip or not, binary option (default: 1 -> skull-strip)

    -  no orientation needed (input image in "standard" orientation), binary option (default: 0 -> orient)


# Command-line

Usage:

    miracl reg mri_allen_nifty -i [ input invivo or exvivo MRI nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -b [ olfactory bulb ] -s [ skull strip ] -n [ no orient needed ]

Example:

    miracl reg mri_allen_nifty -i inv_mri.nii.gz -o RSP -m combined -v 25

arguments (required):

    i.  input MRI nii
        Preferably T2-weighted

optional arguments:

    o.  orient code (default: RSP)
        to orient nifti from original orientation to "standard/Allen" orientation

    m.  hemisphere mirror (default: combined)
        warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
        accepted inputs are: <split> or <combined>

    v.  labels voxel size/Resolution in um (default: 10)
        accepted inputs are: 10, 25 or 50

    l.  input Allen labels to warp (default: annotation_hemi_combined_10um.nii.gz )
        input labels could be at a different depth than default labels

        If l. is specified (m & v cannot be specified)

    b.  olfactory bulb included in brain, binary option (default: 0 -> not included)

    s.  skull strip or not, binary option (default: 1 -> skull-strip)

    f.  FSL skull striping fractional intensity (default: 0.3), smaller values give larger brain outlines

    n.  No orientation needed (input image in "standard" orientation), binary option (default: 0 -> orient)
