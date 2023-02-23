# Tutorials

The tutorial structure generally matches the module/function structure of MIRACL.

In the tutorials, code examples are written as follows:

```
$ miracl -h
```

Code blocks look like this:

```
usage: miracl [-h] {connect,conv,flow,lbls,reg,seg,sta,stats,utils} ...

positional arguments:
  {connect,conv,flow,lbls,reg,seg,sta,stats,utils}
    connect             connectivity functions
    conv                conversion functions
    flow                workflows to run
    lbls                label manipulation functions
    reg                 registration functions
    seg                 segmentation functions
    sta                 structure tensor analysis functions
    stats               statistical functions
    utils               utility functions

optional arguments:
  -h, --help            show this help message and exit
```

Important notes are marked as follows:

> The above -h flag can be used with each of MIRACL's modules/functions

Click on the links below to access the tutorial for the function you are 
interested in or click on [Getting started](./tutorials/beginner/getting_started.md)
for a general introduction tutorial on how to use MIRACL.

> Note that not all functions have tutorials yet...we are working on it!

## General

#### [Getting started](./tutorials/beginner/getting_started.md)

---

## Workflows

#### [CLARITY whole-brain registration to Allen](./tutorials/clar_reg/clar_reg.md)

#### [Structural tensor analysis (STA) on CLARITY-Allen](./tutorials/sta/sta.md)

#### [CLARITY whole-brain segmentation](./tutorials/clar_seg/clar_seg.md)

#### [MRI whole-brain registration to Allen](./tutorials/mri_reg/mri_reg.md)

## Conversion

#### [Tiff to Nii](./tutorials/tiff_to_nii/tiff_to_nii.md)

## Registration

#### [CLARITY-Allen](./tutorials/registration/reg_clarity-allen/reg_clarity-allen.md)

## Utilities

#### [Intensity correction](./tutorials/int_corr/int_corr.md)

---

## HPC

#### [Using MIRACL on Sherlock @ Stanford](./tutorials/sherlock/sherlock.md)

#### [Using MIRACL on Compute Canada (Digital Research Alliance of Canada)](./tutorials/compute_canada/compute_canada.md)
