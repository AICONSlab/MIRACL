# MIRACL 

(Multi-modal Image Registration And Connectivity anaLysis).

## Installation

 - [Local Install](install-local.md) to install the software directly on your host.
 - [Docker Container](install-docker.md) to use our Docker container
 - [Singularity Container](install-singularity.md) to create a Singularity container (safe for HPC)

A [PDF of our documentation](MIRACL_documentation.pdf) is also available. Or skip the words
and go directly to our gallery](gallery.md).

## About

The pipeline is combined of different "Modules" depending on their functionality
Functions for each module are grouped together:
  
 - connect -> Connectivity
 - io -> Input/Output (conversion/orientation) 
 - reg -> Registration
 - seg -> Segmentation 
 - lbls -> Labels 
 - stats -> Statistics


### Flow
The workflow (flow) module combines multiple functions for ease of use to preform a desired task.
For example, for a standard reg/seg analysis a user would run: 
  
```
# First perform registration of whole-brain clarity data to ARA
miracl_workflow_registration_clarity-allen_wb.sh
    

# then perform segmentation & feature extraction of full resolution clarity data  
miracl_workflow_segmentation_clarity.sh
```

### Atlases
The "Atlases" folder contains templates, annotations, histology, ontology graph info & LUT/label description of the Allen reference atlas (ARA)


### Data
The "Data" folder contains test data with example inputs and outputs for the registration and segmentation modules

for a detailed description & input parameters please check the respective README.md of each module 

