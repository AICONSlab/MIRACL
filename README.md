[![GitHub license](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-FFA500.svg?labelColor=lightgrey)](https://github.com/mgoubran/MIRACL/blob/master/LICENSE.md) ![Docker pulls](https://img.shields.io/docker/pulls/mgoubran/miracl) [![CirclCI status](https://img.shields.io/circleci/build/github/AICONSlab/MIRACL)](https://circleci.com/gh/AICONSlab/MIRACL) [![GitHub stars](https://img.shields.io/github/stars/AICONSlab/MIRACL?style=social)](https://github.com/AICONSlab/MIRACL/stargazers)

<p align="center">
  <img src="docs/gallery/images/icon.png" alt="alt text" width="400" height="250"/>
</p>

___

**MIRACL** (**M**ulti-modal **I**mage **R**egistration **A**nd **C**onnectivity ana**L**ysis) is a general-purpose, open-source pipeline for automated:

1. Registration of cleared and imaging data (ex. LSFM and MRI) to atlases (ex. Allen Reference Atlas)
2. 3D Segmentation and feature extraction of cleared data
3. Tract-specific or network-level connectivity analysis
4. Statistical analysis of cleared and imaging data
5. Comparison of dMRI/tractography, virus tracing, and connectivity atlases
6. Atlas generation and Label manipulation

___

\*\***NEW WORKFLOW/FEATURE RELEASE**\*\*

We have released our AI-based Cartography of Ensembles (ACE) workflow, an end-to-end, automated pipeline that integrates cutting-edge deep learning segmentation models and advanced statistical methods to enable unbiased and generalizable brain-wide mapping of 3D alterations in neuronal activity, morphology, or connectivity at the sub-regional and laminar levels beyond atlas-defined regions.

ACE is now available. Tutorials and usage examples for ACE can be found in our [docs](https://miracl.readthedocs.io/en/latest/tutorials/workflows/ace_flow/ace_flow.html). As of MIRACL version `2.4.2` the pre-trained DL models are publicly available and will automatically be downloaded during installation.

___

We recommend using MIRACL with the Docker or Apptainer containers we provide. Legacy instructions for installing MIRACL locally are available but we recommend against it. For more details, see our 
[docs](https://miracl.readthedocs.io).

___

Attention: We changed the license for **MIRACL** from `GPL-3.0` to `CC BY-NC-ND` as of version `2.5.0`. For more information read our [LICENSE.md](LICENSE.md) or go to the [Creative Commons](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en) website.

___
Copyright (c) 2025 Maged Goubran

All Rights Reserved
