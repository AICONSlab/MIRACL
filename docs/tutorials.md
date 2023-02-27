# Tutorials

The tutorial structure generally matches the module/function structure of MIRACL. 
Refer to our tutorials/docs [legend](#legend) for syntax information.

Click on the links below to access the tutorial for the function you are 
interested in or go to our [Getting started](./tutorials/beginner/getting_started.md)
section for a tutorial on MIRACL's general usage.

> Note that not all functions have tutorials yet...we are working on it!

## General

#### [Getting started](./tutorials/beginner/getting_started.md)

## Workflows

#### [CLARITY whole-brain registration to Allen](./tutorials/workflows/clar_reg/clar_reg.md)

#### [Structural tensor analysis (STA) on CLARITY-Allen](./tutorials/workflows/sta/sta.md)

#### [CLARITY whole-brain segmentation](./tutorials/workflows/clar_seg/clar_seg.md)

#### [MRI whole-brain registration to Allen](./tutorials/workflows/mri_reg/mri_reg.md)

## Conversion

#### [Tiff to Nii](./tutorials/tiff_to_nii/tiff_to_nii.md)

## Registration

#### [CLARITY-Allen](./tutorials/registration/reg_clarity-allen/reg_clarity-allen.md)

## Utilities

#### [Intensity correction](./tutorials/int_corr/int_corr.md)

## HPC

#### [Using MIRACL on Sherlock @ Stanford](./tutorials/sherlock/sherlock.md)

#### [Using MIRACL on Compute Canada (Digital Research Alliance of Canada)](./tutorials/compute_canada/compute_canada.md)

## Legend

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

Important notes are marked as blockquotes:

> The above `-h` flag can be used with each of MIRACL's modules/functions

We use brackets to denote text as follows:

- `{}`: Used for variabels.
    - Example: `niftis/downsample{factor}x.nii.gz`
- `<>`: Used for placeholder text in examples that you need to replace with 
your own information.
    - Example: `ssh <username>@cedar.computecanada.ca`
- `[ ]`: Placeholders for flag arguments used in command-line scripting.
    - Example: `miracl flow sta -f [ Tiff folder ] -o [ output nifti ]`
- `[]`: Denotes flags in the command-line help menus.
    - Example: `miracl [-h]`

Code related words or phrases (e.g. file or directory names) are denoted as 
follows: `example_dir/example_file.nii.gz` 

Lastly, links are highlight in blue: [link to MIRACL's README](../README.md)
