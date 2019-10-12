# Modules & Workflows

## Modules

The pipeline is combined of different "Modules" depending on their functionality
Functions for each module are grouped together:

 - connect -> Connectivity
 - conv -> Conversion (Input/Output)
 - reg -> Registration
 - seg -> Segmentation
 - lbls -> Labels
 - utilfn -> Utilities
 - sta -> Structure Tensor Analysis
 - stats -> Statistics

## Workflows
The workflow (flow) module combines multiple functions for ease of use to preform a desired task.
For example, for a standard reg/seg analysis a user would run: 
  
```
# First perform registration of whole-brain clarity data to ARA
miracl flow reg_clar -h
    

# then perform segmentation & feature extraction of full resolution clarity data  
miracl flow seg -h

Or

# perform structure tensor analysis
miracl flow sta -h

```