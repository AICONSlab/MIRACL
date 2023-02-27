# Intensity correction

Intensity correction for data with inhomogeneity issues.
Performs correction on CLARITY tiff data in parallel using N4.

1. Creates a downsampled nifti from the tiff data
2. Runs N4 'bias field'/intensity correction on the nifti
3. Up-samples the output bias field and applies it to the tiff data

## Command-line

Usage:

    miracl utils int_corr -f [ input tiff folder ] -o [ output folder ] -s [ shrink factor] -cn [ channel num ] -cp [ channel prefix ] -p [ power ]

Example:

    miracl utils int_corr -f tiff_folder -od bias_corr_folder

Required arguments:

    -f dir, --folder dir  Input CLARITY TIFF folder/dir

Optional arguments:

    -od , --outdir        Output folder name (default: int_corr_tiffs)
    -cn , --channum       Chan # for extracting single channel from multiple channel data (default: 1)
    -cp , --chanprefix    Chan prefix (string before channel number in file name). ex: C00. (default: None)
    -ch , --channame      Output chan name (default: AAV)
    -on , --outnii        Output nii name (script will append downsample ratio & channel info to given name)
    -vx , --resx          Original resolution in x-y plane in um (default: 5)
    -vz , --resz          Original thickness (z-axis resolution / spacing between slices) in um (default: 5)
    -m , --maskimg        Mask images before correction (default: 1)
    -s , --segment        Perform level-set seg using brain mask to get a dilated one (default: 0)
    -d , --down           Downsample / shrink factor to run bias corr on downsampled data(default: 5)
    -n , --noise          Noise parameter for histogram sharpening - deconvolution (default: 0.005)
    -b , --bins           Histogram bins (default: 200)
    -k , --fwhm           FWHM for histogram sharpening - deconvolution (default: 0.3)
    -l , --levels         Number of levels for convergence (default: 4)
    -it , --iters         Number of iterations per level for convergence (default: 50)
    -t , --thresh         Threshold per iteration for convergence (default: 0)
    -p , --mulpower       Use the bias field raised to a power of 'p' to enhance its effects(default: 1.0)

---

[<- back to tutorials](../../tutorials.md)
