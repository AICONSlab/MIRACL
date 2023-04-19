Intensity correction
####################

Intensity correction for data with inhomogeneity issues.
Performs correction on CLARITY tiff data in parallel using N4.

#. Creates a downsampled nifti from the tiff data
#. Runs N4 'bias field'/intensity correction on the nifti file
#. Up-samples the output bias field and applies it to the tiff data

Command-line
============

Usage:

.. code-block::

   $ miracl utils int_corr -f [ input_tiff_folder ] -od [ output_folder ] -s [ shrink_factor] -cn [ channel_num ] -cp [ channel_prefix ] -p [ power ]

Example:

.. code-block::

   $ miracl utils int_corr -f tiff_folder -od bias_corr_folder

Required arguments:

.. table::

   ============  =============================  ==================================================
   Flags         Description                    Default                                                                       Default
   ============  =============================  ==================================================
   -f, --folder  Input CLARITY TIFF folder/dir  No default. Input folder must be provided by user.
   ============  =============================  ==================================================

Optional arguments:

.. table::

   ===================  ==================================================================================  ==================
   Flags                Description                                                                         Default
   ===================  ==================================================================================  ==================
   -od, \-\-outdir      Output folder name                                                                  ``int_corr_tiffs``
   -cn, \-\-channum     Chan # for extracting single channel from multiple channel                          ``data  1``
   -cp, \-\-chanprefix  Chan prefix (string before channel number in file name). Example: ``C00``           ``None``
   -ch, \-\-channame    Output chan name                                                                    ``AAV``
   -on, \-\-outnii      Output nii name (script will append downsample ratio & channel info to given name)
   -vx, \-\-resx        Original resolution in x-y plane in                                                 ``um  5``
   -vz, \-\-resz        Original thickness (z-axis resolution/spacing between slices) in um                 ``5``
   -m, \-\-maskimg      Mask images before                                                                  ``correction  1``
   -s, \-\-segment      Perform level-set seg using brain mask to get a dilated                             ``one  0``
   -d, \-\-down         Downsample/shrink factor to run bias corr on downsampled                            ``data 5``
   -n, \-\-noise        Noise parameter for histogram sharpening - deconvolution                            ``0.005``
   -b, \-\-bins         Histogram bins                                                                      ``200``
   -k, \-\-fwhm         FWHM for histogram sharpening - deconvolution                                       ``0.3``
   -l, \-\-levels       Number of levels for                                                                ``convergence  4``
   -it, \-\-iters       Number of iterations per level for convergence                                      ``50``
   -t, \-\-thresh       Threshold per iteration for                                                         ``convergence  0``
   -p, \-\-mulpower     Use the bias field raised to a power of ``p`` to enhance its effects                ``1.0``
   ===================  ==================================================================================  ==================
