# MRI whole-brain registration to Allen atlas

This workflow performs the following tasks:

1) Registers in-vivo or ex-vivo MRI data to Allen Reference mouse brain Atlas
2) Warps Allen annotations to the MRI space

## GUI

Invoke with `$ miraclGUI` and select from main menu or run:

```
$ miracl reg mri_allen_nifty
```

The following window will open:

![](reg_options.png)

Click on `Select In-vivo or Ex-vivo MRI` and choose the input MRI nii 
(preferable T2-w) using the dialog window. Then set the registration options:

| Parameter | Description | Default |
| ---       | ---         | ---     |
| Orient code | Orient nifti from original orientation to "standard/Allen" orientation. | `RSP` |
| Labels Hemi | Warp allen labels with hemisphere split (Left different than Right labels) or combined (Left and Right labels are the same/mirrored). Accepted inputs are: <ul><li>`split`</li><li>`combined`</li></ul> | `combined` |
| Labels resolution [vox] | Labels voxel size/resolution in um. Accepted inputs are: <ul><li>`10`</li><li>`25`</li><li>`50`</li></ul> | `10` |
| Olfactory bulb included | Specify whether the olfactory bulb is included in brain. Accepted inputs are: <ul><li>`0` (not included)</li><li>`1` (included)</li></ul> | `0` |
| skull strip | Strip skull. Accepted inputs are: <ul><li>`0` (don't strip)</li><li>`1` (strip)</li></ul> | `1` |
| No orient | No orientation needed (input image in "standard" orientation). Accepted inputs are: <ul><li>`0` (orient)</li><li>`1` (don't orient)</li></ul> | `0` |

Click `Enter` and `Run` to start the registration process.

## Command-line

Usage:

```
$ miracl reg mri_allen_nifty -i [ input invivo or exvivo MRI nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -b [ olfactory bulb ] -s [ skull strip ] -n [ no orient needed ]
```

Example:

```
$ miracl reg mri_allen_nifty -i inv_mri.nii.gz -o RSP -m combined -v 25
```

Arguments:

```
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
```

---

[<- back to tutorials](../../tutorials.md)
