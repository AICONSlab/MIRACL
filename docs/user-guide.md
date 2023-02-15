# User guide

MIRACL is structured into [Modules](#modules) and [Workflows](#workflows).

## Modules

The pipeline is comprised of different "Modules" depending on their 
respective functionality. Functions for each module are grouped together:

- connect -> Connectivity
- conv -> Conversion (Input/Output)
- reg -> Registration
- seg -> Segmentation
- lbls -> Labels
- utilfn -> Utilities
- sta -> Structure Tensor Analysis
- stats -> Statistics

On the command-line, the `-h` flag can be used to get help on each module. For 
example, to show all functions of the `reg` module run:

```
$ miracl reg -h
```

To show all options for an individual function, e.g. the `clar_allen` function,
you can run:

```
$ miracl reg clar_allen -h
```

An example of using a module would be to run the above `clar_allen` function 
which performs a CLARITY whole-brain registration to Allen Atlas on a `nifti` 
image (down-sampled by a factor of five):

```
$ miracl reg clar_allen -i niftis/SHIELD_05x_down_autoflor_chan.nii.gz -o ARI -m combined -b 1
```

The above command uses the `-i` option to select the `nifti` file, `-o` to 
specify the orientation of the image, `-m` to register to both hemispheres and 
`-b` to include the olfactory bulb.

## Workflows

The workflow (`flow`) module combines multiple functions from the above modules 
for ease of use to preform a desired task.

For example, a standard reg/seg analysis could look like this: 
  
```
# First perform registration of whole-brain clarity data to ARA
$ miracl flow reg_clar -h
    
# Then perform segmentation & feature extraction of full resolution clarity data  
$ miracl flow seg -h

Or:

# Perform structure tensor analysis
$ miracl flow sta -h
```
