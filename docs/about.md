# About

This is the place to get useful information about MIRACL. Jump to a topic you 
are interested in by chosing it from the sidebar menu.

## MIRACL in a nutshell

MIRACL (Multi-modal Image Registration And Connectivity anaLysis) is a 
general-purpose, open-source pipeline for automated:

1) Registration of mice clarity data to the Allen reference atlas
2) Segmentation & feature extraction of mice clarity data in 3D (Sparse & nuclear staining)
3) Registration of mice multimodal imaging data (MRI & CT, in-vivo & ex-vivo) to Allen reference atlas
4) Tract or label specific connectivity analysis based on the Allen connectivity atlas
5) Comparison of diffusion tensort imaging (DTI)/tractography, virus tracing using CLARITY &
   Allen connectivity atlas
6) Statistical analysis of CLARITY & Imaging data
7) Atlas generation & Label manipulation

### Program structure

MIRACL is structured into [Modules](#modules) and [Workflows](#workflows).

#### Modules

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

An example of using a module would be to run the `clar_allen` function 
which performs a CLARITY whole-brain registration to Allen Atlas on a `nifti` 
image (down-sampled by a factor of five):

```
$ miracl reg clar_allen -i niftis/SHIELD_05x_down_autoflor_chan.nii.gz -o ARI -m combined -b 1
```

The above command uses the `-i` option to select the `nifti` file, `-o` to 
specify the orientation of the image, `-m` to register to both hemispheres and 
`-b` to include the olfactory bulb.

#### Workflows

The workflow (`flow`) module combines multiple functions from the above modules 
for ease of use to preform a desired task.

For example, a standard reg/seg analysis could look like this: 
  
1. First perform registration of whole-brain clarity data to ARA:

```
$ miracl flow reg_clar -h
```
    
2. Then perform segmentation & feature extraction of full resolution clarity data:

```
$ miracl flow seg -h
```

Or structure tensor analysis:

```
$ miracl flow sta -h
```

## License

MIRACL is licensed under the terms of the [GNU General
Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

MIRACL is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
You should have received a copy of GNU General Public 
License v3.0 along with [HippMapp3r](https://github.com/AICONSlab/HippMapp3r). 

The code is released for academic research use only. For 
commercial use, please contact 
[maged.goubran@sri.utoronto.ca](mailto:maged.goubran@sri.utoronto.ca).

## Referencing MIRACL

Citation guidelines for using MIRACL in your work.

### MIRACL publication

If you use MIRACL in your work please cite our
[paper](https://www.nature.com/articles/s41467-019-13374-0).

APA:

Goubran, M., Leuze, C., Hsueh, B., Aswendt, M., Ye, L., 
Tian, Q., Cheng, M.Y., Crow, A., Steinberg, G.K., McNab, J.A., 
Deisseroth, K., and Zeineh, M. (2019). Multimodal image 
registration and connectivity analysis for integration of 
connectomic data from microscopy to MRI. Nature communications, 
10(1), 5504.

BibTeX:

```
@article{goubran2019multimodal,
  title={Multimodal image registration and connectivity analysis for integration of connectomic data from microscopy to MRI},
  author={Goubran, Maged and Leuze, Christoph and Hsueh, Brian and Aswendt, Markus and Ye, Li and Tian, Qiyuan and Cheng, Michelle Y and Crow, Ailey and Steinberg, Gary K and McNab, Jennifer A and Deisseroth, Karl and Zeineh, Michael},
  journal={Nature communications},
  volume={10},
  number={1},
  pages={5504},
  year={2019},
  publisher={Nature Publishing Group UK London}
}
```

### Tools used by MIRACL

Some of our functions build on or use these tools (please cite 
their work if you are using them):

 - [Allen Regional Atlas](http://mouse.brain-map.org/static/atlas) (for atlas registration)
 - [Allen Connectivity Atlas](http://connectivity.brain-map.org/) (for connectivity analyses)
 - [ANTs](https://github.com/stnava/ANTs) (for registration)
 - [Fiji](https://imagej.nih.gov/ij/index.html) (for segmentation)
 - [c3d](https://sourceforge.net/projects/c3d) (for image processing)
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki) (for diffusion MRI processing)
 - [MRtrix3](https://mrtrix.readthedocs.io/en/latest/) (for tractography)
 - [TrackVis/DTK](http://trackvis.org/) (for tractography)

## Citations

A selection of publications that used or referenced MIRACL:

- Boillat, M., Hammoudi, P. M., Dogga, S. K., Pages, S., Goubran, M.,
Rodriguez, I., & Soldati-Favre, D. (2020). Neuroinflammation-associated 
aspecific manipulation of mouse predator fear by Toxoplasma gondii. Cell 
reports, 30(2), 320-334.

- Pallast, N., Wieters, F., Nill, M., Fink, G. R., & Aswendt, M. (2020).
[Graph theoretical quantification of white matter reorganization after cortical
stroke in mice](https://www.sciencedirect.com/science/article/pii/S1053811920303591).
NeuroImage, 217, 116873.

- Qu, L., Li, Y., Xie, P., Liu, L., Wang, Y., Wu, J., ... & Peng, H. (2022). 
Cross-modal coherent registration of whole mouse brains. Nature Methods, 
19(1), 111-118.

- Ito, M., Aswendt, M., Lee, A. G., Ishizaka, S., Cao, Z., Wang, E. H., ... &
Steinberg, G. K. (2018). [RNA-sequencing analysis revealed a distinct motor 
cortex transcriptome in spontaneously recovered mice after stroke](https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.021508).
Stroke, 49(9), 2191-2199.

- Georgiadis, M., Schroeter, A., Gao, Z., Guizar-Sicairos, M., Liebi, M., 
Leuze, C., ... & Rudin, M. (2021). [Nanostructure-specific X-ray tomography 
reveals myelin levels, integrity and axon orientations in mouse and human 
nervous tissue](https://www.nature.com/articles/s41467-021-22719-7). Nature 
communications, 12(1), 2941.

- Wang, X., Zeng, W., Yang, X., Zhang, Y., Fang, C., Zeng, S., ... & Fei, P.
(2021). [Bi-channel image registration and deep-learning segmentation (BIRDS)
for efficient, versatile 3D mapping of mouse brain](https://elifesciences.org/articles/63455.pdf). 
Elife, 10, e63455.

## Collaborators

A list of research labs that use MIRACL for their work:

## Acknowledgements

Huge thank you to:

 - Vanessa Sochat (@vsoch) for creating the Docker & Singularity
 containers for the pipeline
 - Newton Cho, Jordan Squair & Stéphane Pagès for helping 
 optimize the segmentation workflows & troubleshooting

GitHub contributers:

- [mgrouban](https://github.com/mgoubran)
- [entiri](https://github.com/entiri)
- [jono3030](https://github.com/jono3030)
- [vsoch](https://github.com/vsoch)
- [ishita1988](https://github.com/ishita1988)
- [chrisroat](https://github.com/chrisroat)

## AICONS Lab

The **A**rtificial **I**ntelligence and **CO**mputational
**N**euro**S**ciences (AICONS) Lab is located at the Sunnybrook
Research Institute of the University of Toronto and is part of the
Black Centre for Brain Resilience and Recovery, Harquail Centre for 
Neuromodulation, and Temerty Centre for AI Research and Education in 
Medicine.

Our work combines technical and translational research, focusing 
on the development of novel AI, computational and imaging tools to 
probe, predict and understand neuronal and vascular circuit 
alterations, and model brain pathology in neurological disorders, 
including Alzheimer’s disease, stroke and traumatic brain injury.

For more information visit our official [webpage](https://aiconslab.github.io/).
