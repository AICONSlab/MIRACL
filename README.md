[![GitHub license](https://img.shields.io/github/license/mgoubran/MIRACL)](https://github.com/mgoubran/MIRACL/blob/master/LICENSE.md) ![Docker Pulls](https://img.shields.io/docker/pulls/mgoubran/miracl)

<p align="center">
  <img src="docs/gallery/images/icon.png" alt="alt text" width="400" height="250"/>
</p>

___

MIRACL (Multi-modal Image Registration And Connectivity anaLysis)
is a general-purpose, open-source pipeline for automated:

1) Registration of mice clarity data to the Allen reference atlas
2) Segmentation & feature extraction of mice clarity data in 3D (Sparse & nuclear staining)
3) Registration of mice multimodal imaging data (MRI & CT, in-vivo & ex-vivo) to Allen reference atlas
4) Tract or label specific connectivity analysis based on the Allen connectivity atlas
5) Comparison of diffusion tensort imaging (DTI)/tractography, virus tracing using CLARITY &
   Allen connectivity atlas
6) Statistical analysis of CLARITY & Imaging data
7) Atlas generation & Label manipulation

Copyright (c) 2022 Maged Goubran, maged.goubran@utoronto.ca

All Rights Reserved

___

We provide containers for using the software (Docker and Singularity) as well as
local install instructions. For more details, see our [docs](https://miracl.readthedocs.io). 
Note that the base image for the docker container can be found in [docker](docker) and
the container `mgoubran/miracl` is built on top of that.
