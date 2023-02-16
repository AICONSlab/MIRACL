# CLARITY-Allen registration

1. Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
2. Warps Allen annotations to the original high-res CLARITY space
3. Warps the higher-resolution CLARITY to Allen space

## GUI

To open the main registration menu, open MIRACL's main menu first by running:

```
$ miraclGUI
```

MIRACL's main menu will open:

![MIRACL's main menu](../../../gallery/menus/MIRACL_main-menu.png)

Select the Registration tab on the left for the main registration menu.

To open the main registration menu directly, run:

```
$ miracl reg clar_allen
```

The main registration window will look like this:

![Main registration menu](../../../gallery/menus/MIRACL_registration_main-menu.png)

From here you can select `CLARITY-Allen` from the `Registration` tab on the
left to start the registration. The `CLARITY-Allen` menu will open:

![CLARITY-Allen registration menu](../../../gallery/menus/MIRACL_registration_clar-allen-menu.png)

The registration will be run on down-sampled CLARITY Nii images:

- *-i*,  **Input down-sampled CLARITY Nii**: preferably auto-fluorescence
channel data (or Thy1_EYFP if no auto chan). File name should have `##x_down`
like `05x_down` (meaning 5x downsampled) -> ex.:
`stroke13_05x_down_Ref_chan.nii.gz` (this should be accurate as it is used for
Allen label upsampling to clarity).

You can provide the folder containing these files in the first field. **This
parameter is required to run the registration.** If you do not yet have the 
down-sampled files you can use MIRACL's conversion methods to create them.

All remaining parameters are optional. If left blank, their respective default
values will be used:

- *-r*, **Output directory**: directory the output (results) will be written to
(default: `<working_directory>/reg_final`).

- *-o*, **Orient code**: code to orient nifti from original orientation to
'standard/Allen' orientation (default: `ALS`).

- *-m*, **Labels hemi**: chose to register to one or both hemispheres. Warps
Allen labels with hemisphere split (L differ from R labels) or combined
(L and R have the same labels i.e. are mirrored). Accepted inputs are
`combined` or `split` (default: `combined`).

- *-v*, **Labels resolution [vox]**: labels voxel size/resolution in $\mu$m
accepted inputs are: `10`, `25` or `50` (default: `10`).

- *-b*, **Olfactory bulb included**: specify whether the olfactory bulb is
included in brain. Accepted inputs are `0` (not included) and `1` (included)
(default: `0`).

- *-s*, **Side**: provide this parameter if you are only registering one
hemisphere instead of the whole brain. Accepted inputs are `rh`
(right hemisphere) or `lh` (left hemisphere) (default: `None`).

- *-p*, **Extra int correct**: if utilfn intensity correction has already been
run, skip correction inside registration (default: `0`).

After providing the parameters click `Enter` to save them and `Run` to 
start the registration process.

Once the registration is done the final files will be located in the output 
folder (default: `<working_directory>/reg_final`). Files created in intermediate 
steps will be located in a folder called `clar_allen_reg`.

---

## Command-line

The command-line version has additional functionality that is not included in 
the GUI version:

- *-l*, **Input Allen labels to warp**: input labels could be at a different depth
than default labels. `-m` and `-v` flags cannot be used if this parameter is 
specified manually (default: `annotation_hemi_combined_10um.nii.gz`).

- *-a*, **Input custom Allen atlas**: for example for registering sections.

- *-f*, Save mosaic figure (`.png`) of Allen labels registered to
CLARITY (default: 1).

- *-w*, Warp high-res clarity to Allen space (default: 0).

**Note that the above listed `-i` parameter (input down-sampled CLARITY Nii) is 
required.**

Usage:

```
$ miracl reg clar_allen -i <input_clarity_nii_folder> -o <orientation_code> -m <hemispheres> -v <labels_resolution> -l <input_labels> -s <side_if_hemisphere_only> -b <olfactory_buld_included>
```

Example:

```
$ miracl reg clar_allen -i downsampled_niftis/SHIELD_03x_down_autoflor_chan.nii.gz -o ARI -m combined -b 1
```