MAPL3 Workflow
##############

**M**\ apping **A**\ xonal **P**\ rojections in **L**\ ight-sheet Fluorescence Microscopy in **3**\ D

Summary and key highlights
==========================

MAPL3 is an end-to-end deep learning pipeline for generalizable, brain-wide mapping of structural connectivity at the single-axon level using tera-voxel light sheet fluorescence microscopy (LSFM) dataset. It's uilt for scalability, precision, and biological insight, MAPL3 bridges the gap between raw LSFM data and interpretable brain-wide connectivity maps.

- **Hybrid CNN–Transformer Architecture**: A novel deep learning design that fuses convolutional precision with transformer-level context awareness, capturing both fine axonal details and global anatomical structure.
- **Self-Supervised Generative Pretraining**: Pretrained on 22,000+ 3D sub-volumes using advanced self-supervised learning (SSL) and unique patch-based augmentation strategies. Enhances model robustness across diverse imaging conditions and experimental setups.
- **State-of-the-Art Performance**: Extensively benchmarked against leading DL pipelines, MAPL3 consistently outperforms them in both in- and out-of-distribution datasets, from patch-level inference to full-brain reconstructions.
- **Neuroscientific Discovery at Scale**: MAPL3 reveals cell-type-specific axonal connectivity patterns previously unresolved by existing methods, enabling new insights into mesoscale and quantitative brain circuitry analysis.

Installation
============

To install the :program:`MAPL3` workflow, refer to the MIRACL installation guide:

- :doc:`Installation guide <../../../installation/installation>`
