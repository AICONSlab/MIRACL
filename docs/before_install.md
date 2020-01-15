# Before installing MIRACL

## License

MIRACL is licensed under the terms of the *GNU General Public License v3.0*.

MIRACL is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of GNU General Public License v3.0 along with HippMapp3r. 

The code is released for academic research use only. For commercial use, please contact [maged.goubran@sri.utoronto.ca](mailto:maged.goubran@sri.utoronto.ca).

## Reference

If you use MIRACL in your work please cite our [paper](https://www.nature.com/articles/s41467-019-13374-0):

Goubran, M., Leuze, C., Hsueh, B., Aswendt, M., Ye, L., Tian, Q., Cheng, M.Y., Crow, A., Steinberg, G.K., McNab, J.A., Deisseroth, K., and Zeineh, M. “Multimodal image registration and connectivity analysis for integration of connectomic data from microscopy to MRI.” Nature communications. 2019. 

Some of our functions build on or use these tools (please cite their work if you are using them):

 - [Allen Regional Atlas](http://mouse.brain-map.org/static/atlas) (for atlas registration)
 - [Allen Connectivity Atlas](http://connectivity.brain-map.org/) (for connectivity analyses)
 - [ANTs](https://github.com/stnava/ANTs) (for registration)
 - [Fiji](https://imagej.nih.gov/ij/index.html) (for segmentation)
 - [c3d](https://sourceforge.net/projects/c3d) (for image processing)
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki) (for diffusion MRI processing)
 - [MRtri3](https://mrtrix.readthedocs.io/en/latest/) (for tractography)

## Acknowledgements
Huge thank you to:

 - Vanessa Sochat (@vsoch) for creating the Docker & Singularity containers for the pipeline
 - Newton Cho, Jordan Squair & Stéphane Pagès for helping optimize the segmentation workflows & troubleshooting

