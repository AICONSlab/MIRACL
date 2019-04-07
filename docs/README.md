## About

<p align="center">
  <img src="gallery/icon.png" alt="alt text" width="400" height="250"/>
</p>


MIRACL is a general-purpose, open-source pipeline for automated:

	1) Registration of mice clarity data to the Allen reference atlas

	2) Segmentation & feature extraction of mice clarity data in 3D (Sparse & nuclear staining)

	3) Registration of mice multimodal imaging data (MRI & CT, in-vivo & ex-vivo) to Allen reference atlas

	4) Label or region specific connectivity analysis based on the Allen connectivity atlas

    5) Comparison of diffusion tensort imaging (DTI)/tractography, virus tracing using CLARITY &
      Allen connectivity atlas

    6) Statistical analysis of CLARITY & Imaging data

	7) Atlas generation & Label manipulation

## Installation

 - [Local Install](install-local.md) to install the software directly on your host.
 - [Docker Container](install-docker.md) to use our Docker container (coming soon)
 - [Singularity Container](install-singularity.md) to create a Singularity container (safe for HPC) (coming soon)


## Tutorials

- [Clarity registration workflow](tutorials/clar_reg/clar_reg.md)
- [Clarity segmentation workflow](tutorials/clar_seg/clar_seg.md)
- [Structural tensor analysis (STA) workflow](tutorials/sta/sta.md)
- [MRI registration workflow](tutorials/mri_reg/mri_reg.md)
- [Tiff to NII conversion](tutorials/tiff_to_nii/tiff_to_nii.md)
- [Intensity correction](tutorials/int_corr/int_corr.md)

## Documentation

A [PDF of our documentation](MIRACL_documentation.pdf) is available.


## Gallery

Or skip the words and go directly to our [gallery](gallery.md).


## Modules

The pipeline is combined of different "Modules" depending on their functionality
Functions for each module are grouped together:

 - connect -> Connectivity
 - io -> Input/Output (conversion/orientation)
 - reg -> Registration
 - seg -> Segmentation
 - lbls -> Labels
 - utils -> Utilities
 - sta -> Structure Tensor Analysis
 - stats -> Statistics

#### Workflows
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

## Data

Example and atlases data are found here:

https://stanfordmedicine.app.box.com/s/6kx5tfgbqd6ruk7uo0u64agn4oqpg39i

The **Atlases** folder contains templates, annotations, histology, ontology graph info & LUT/label description of the Allen reference atlas (ARA)

The **Data** folder contains test data with example inputs and outputs for the registration and segmentation modules

for a detailed description & input parameters please check the respective README.md of each module 


## Troubleshooting

check reported issues (coming soon)


## Acknowledgements
Huge thank you to:

 - Vanessa Sochat (@vsoch) for creating the Docker & Singularity containers for the pipeline
 - Newton Cho, Jordan Squair & Stéphane Pagès for helping optimize the segmentation workflows & troubleshooting


## References

 - (coming soon)
 - ANTs
 - c3d
 - FSL