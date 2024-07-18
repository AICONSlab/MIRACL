from typing import Optional

from PyQt5.QtWidgets import (QDialog, QPushButton, QTextEdit, QVBoxLayout,
                             QWidget)


class HelpMessageBox(QDialog):
    docs_message = """<b>The full documentation for the ACE flow can be found at the following URL:</b>
<br>
<br>

<a href="https://miracl.readthedocs.io/en/latest/tutorials/workflows/ace_flow/ace_flow.html" target="_blank">
https://miracl.readthedocs.io/en/latest/tutorials/workflows/ace_flow/ace_flow.html
</a>
<br>
"""
    parameter_description="""
single or multi method arguments:
  user is required to pass either single or multi method arguments

  -s SINGLE_TIFF_DIR, --single SINGLE_TIFF_DIR
                        path to single raw tif/tiff data folder
  -c CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE, --control CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE
                        FIRST: path to base control directory. SECOND: example
                        path to control subject tiff directory
  -t TREATED_BASE_DIR TREATED_TIFF_DIR_EXAMPLE, --treated TREATED_BASE_DIR TREATED_TIFF_DIR_EXAMPLE
                        FIRST: path to base treated directory. SECOND: example
                        path to treated subject tiff directory

required arguments:
  (set the single or multi method arguments first)

  -sao SA_OUTPUT_FOLDER, --sa_output_folder SA_OUTPUT_FOLDER
                        path to output file folder
  -sam {unet,unetr,ensemble}, --sa_model_type {unet,unetr,ensemble}
                        model architecture
  -sar X-res Y-res Z-res, --sa_resolution X-res Y-res Z-res
                        voxel size (type: float)

useful/important arguments:
  -sag SA_GPU_INDEX, --sa_gpu_index SA_GPU_INDEX
                        index of the GPU to use (type: int; default: 0)
  -ctnd CTN_DOWN, --ctn_down CTN_DOWN
                        Down-sample ratio for conversion (default: 5)
  -rcao RCA_ORIENT_CODE, --rca_orient_code RCA_ORIENT_CODE
                        to orient nifti from original orientation to
                        'standard/Allen' orientation, (default: ALS)
  -rcav {10,25,50}, --rca_voxel_size {10,25,50}
                        labels voxel size/Resolution in um (default: 10)
  -rvad RVA_DOWNSAMPLE, --rva_downsample RVA_DOWNSAMPLE
                        downsample ratio for voxelization, recommended: 5 <=
                        ratio <= 10 (default: 10)
  -rwcv {10,25,50}, --rwc_voxel_size {10,25,50}
                        voxel size/Resolution in um for warping (default: 25)
  --rerun-registration TRUE/FALSE
                        whether to rerun registration step of flow; TRUE =>
                        Force re-run (default: false)
  --rerun-segmentation TRUE/FALSE
                        whether to rerun segmentation step of flow; TRUE =>
                        Force re-run (default: false)
  --rerun-conversion TRUE/FALSE
                        whether to rerun conversion step of flow; TRUE =>
                        Force re-run (default: false)

optional segmentation arguments:
  -sas height width depth, --sa_image_size height width depth
                        image size (type: int; default: fetched from image
                        header)
  -saw SA_NR_WORKERS, --sa_nr_workers SA_NR_WORKERS
                        number of cpu cores deployed to pre-process image
                        patches in parallel (type: int; default: 4)
  -sac SA_CACHE_RATE, --sa_cache_rate SA_CACHE_RATE
                        percentage of raw data that is loaded into cpu during
                        segmentation (type: float; default: 0.0)
  -sab SA_BATCH_SIZE, --sa_batch_size SA_BATCH_SIZE
                        number of image patches being processed by the model
                        in parallel on gpu (type: int; default: 4)
  -samc SA_MONTE_CARLO, --sa_monte_carlo SA_MONTE_CARLO
                        use Monte Carlo dropout (default: 0)
  -sav, --sa_visualize_results
                        visualizing model output after predictions (default:
                        False)
  -sau, --sa_uncertainty_map
                        enable map (default: False)
  -sat SA_BINARIZATION_THRESHOLD, --sa_binarization_threshold SA_BINARIZATION_THRESHOLD
                        threshold value for binarization (type: float;
                        default: 0.5)
  -sap SA_PERCENTAGE_BRAIN_PATCH_SKIP, --sa_percentage_brain_patch_skip SA_PERCENTAGE_BRAIN_PATCH_SKIP
                        percentage threshold of patch that is brain to skip
                        during segmentation (type: float; default: 0.0)

optional conversion arguments:
  -ctncn , --ctn_channum 
                        Chan # for extracting single channel from multiple
                        channel data (default: 0)
  -ctncp , --ctn_chanprefix 
                        Chan prefix (string before channel number in file
                        name). ex: C00
  -ctnch , --ctn_channame 
                        Output chan name (default: auto). Channel used in
                        registration.
  -ctno , --ctn_outnii 
                        Output nii name (script will append downsample ratio &
                        channel info to given name). Method of tissue
                        clearing.
  -ctnc  [ ...], --ctn_center  [ ...]
                        Nii center (default: 0 0 0 ) corresponding to Allen
                        atlas nii template
  -ctndz , --ctn_downzdim 
                        Down-sample in z dimension, binary argument, (default:
                        1) => yes
  -ctnpd , --ctn_prevdown 
                        Previous down-sample ratio, if already downs-sampled
  -ctnpct , --ctn_percentile_thr 
                        Percentile threshold for intensity correction
                        (default: 0.01)

optional registration arguments:
  -rcam {combined,split}, --rca_hemi {combined,split}
                        warp allen labels with hemisphere split (Left
                        different than Right labels) or combined (L & R same
                        labels/Mirrored) (default: combined)
  -rcal RCA_ALLEN_LABEL, --rca_allen_label RCA_ALLEN_LABEL
                        input Allen labels to warp. Input labels could be at a
                        different depth than default labels, If l. is
                        specified (m & v cannot be specified) (default: None)
  -rcaa RCA_ALLEN_ATLAS, --rca_allen_atlas RCA_ALLEN_ATLAS
                        custom Allen atlas (default: None)
  -rcas {rh,lh}, --rca_side {rh,lh}
                        side, if only registering a hemisphere instead of
                        whole brain (default: None)
  -rcanm, --rca_no_mosaic_fig
                        by default a mosaic figure (.png) of allen labels
                        registered to clarity will be saved. If this flag is
                        set, the mosaic figure will not be saved.
  -rcab {0,1}, --rca_olfactory_bulb {0,1}
                        include olfactory bulb in brain (default: 0)
  -rcap, --rca_skip_cor
                        if utilfn intensity correction already ran, skip
                        correction inside registration (default: 0)
  -rcaw, --rca_warp     warp high-res clarity to Allen space (default: False)

optional voxelization arguments:
  -rvavx RVA_VX_RES, --rva_vx_res RVA_VX_RES
                        voxel size (x, y dims) in um (default: 1)
  -rvavz RVA_VZ_RES, --rva_vz_res RVA_VZ_RES
                        voxel size (z dim) in um (default: 1)

optional warping arguments:
  -rwcr RWC_INPUT_FOLDER, --rwc_input_folder RWC_INPUT_FOLDER
                        path to CLARITY registration folder
  -rwcn RWC_INPUT_NII, --rwc_input_nii RWC_INPUT_NII
                        path to downsampled CLARITY nii file to warp
  -rwcc RWC_SEG_CHANNEL, --rwc_seg_channel RWC_SEG_CHANNEL
                        Segmentation channel (ex. green) - required if
                        voxelized seg is input

optional cluster-wise arguments:
  -pcsa PCS_ATLAS_DIR, --pcs_atlas_dir PCS_ATLAS_DIR
                        path of atlas directory
  -pcsn PCS_NUM_PERM, --pcs_num_perm PCS_NUM_PERM
                        number of permutations (default: 500)
  -pcsr PCS_IMG_RESOLUTION, --pcs_img_resolution PCS_IMG_RESOLUTION
                        resolution of images in um (default: 25)
  -pcsfwhm PCS_SMOOTHING_FWHM, --pcs_smoothing_fwhm PCS_SMOOTHING_FWHM
                        fwhm of Gaussian kernel in pixel (default: 3)
  -pcsstart PCS_TFCE_START, --pcs_tfce_start PCS_TFCE_START
                        tfce threshold start (default: 0.01)
  -pcsstep PCS_TFCE_STEP, --pcs_tfce_step PCS_TFCE_STEP
                        tfce threshold step (default: 5)
  -pcsc PCS_CPU_LOAD, --pcs_cpu_load PCS_CPU_LOAD
                        Percent of cpus used for parallelization (default:
                        0.9)
  -pcsh PCS_TFCE_H, --pcs_tfce_h PCS_TFCE_H
                        tfce H power (default: 2)
  -pcse PCS_TFCE_E, --pcs_tfce_e PCS_TFCE_E
                        tfce E power (default: 0.5)
  -pcssp PCS_STEP_DOWN_P, --pcs_step_down_p PCS_STEP_DOWN_P
                        step down p-value (default: 0.3)
  -pcsm PCS_MASK_THR, --pcs_mask_thr PCS_MASK_THR
                        percentile to be used for binarizing difference of the
                        mean (default: 95)

optional correlation arguments:
  -cft CF_PVALUE_THR, --cf_pvalue_thr CF_PVALUE_THR
                        threshold for binarizing p value (default: 0.05)

optional heatmap arguments:
  -shg1 SH_GROUP1, --sh_group1 SH_GROUP1
                        path to group 1 directory
  -shg2 SH_GROUP2, --sh_group2 SH_GROUP2
                        path to group 2 directory
  -shv {10,25,50}, --sh_vox {10,25,50}
                        voxel size/Resolution in um
  -shgs SH_SIGMA, --sh_sigma SH_SIGMA
                        Gaussian smoothing sigma (default: 4)
  -shp SH_PERCENTILE, --sh_percentile SH_PERCENTILE
                        percentile (%) threshold for registration-to-input
                        data check svg animation (default: 10)
  -shcp SH_COLOURMAP_POS, --sh_colourmap_pos SH_COLOURMAP_POS
                        matplotlib colourmap for positive values (default:
                        Reds)
  -shcn SH_COLOURMAP_NEG, --sh_colourmap_neg SH_COLOURMAP_NEG
                        matplotlib colourmap for negative values (default:
                        Blues)
  -shs SH_SAGITTAL SH_SAGITTAL SH_SAGITTAL SH_SAGITTAL SH_SAGITTAL, --sh_sagittal SH_SAGITTAL SH_SAGITTAL SH_SAGITTAL SH_SAGITTAL SH_SAGITTAL
                        slicing across sagittal axis. 5 Arguments: start_slice
                        slice_interval number_of_slices number_of_rows
                        number_of_columns
  -shc SH_CORONAL SH_CORONAL SH_CORONAL SH_CORONAL SH_CORONAL, --sh_coronal SH_CORONAL SH_CORONAL SH_CORONAL SH_CORONAL SH_CORONAL
                        slicing across coronal axis. 5 Arguments: start_slice
                        interval number_of_slices number_of_rows
                        number_of_columns
  -sha SH_AXIAL SH_AXIAL SH_AXIAL SH_AXIAL SH_AXIAL, --sh_axial SH_AXIAL SH_AXIAL SH_AXIAL SH_AXIAL SH_AXIAL
                        slicing across axial axis. 5 Arguments: start_slice
                        interval number_of_slices number_of_rows
                        number_of_columns
  -shf SH_FIGURE_DIM SH_FIGURE_DIM, --sh_figure_dim SH_FIGURE_DIM SH_FIGURE_DIM
                        figure width and height
  -shd SH_DIR_OUTFILE, --sh_dir_outfile SH_DIR_OUTFILE
                        Output file directory (default: /home/arinaldi)
  -sho SH_OUTFILE [SH_OUTFILE ...], --sh_outfile SH_OUTFILE [SH_OUTFILE ...]
                        Output filenames (default: ['group_1', 'group_2',
                        'group_difference'])
  -she SH_EXTENSION, --sh_extension SH_EXTENSION
                        heatmap figure extension (default: tiff)
  -shdpi SH_DPI, --sh_dpi SH_DPI
                        dots per inch (default: 500)

optional statistics arguments:
  -ua U_ATLAS_DIR, --u_atlas_dir U_ATLAS_DIR
                        path of atlas directory (default: /code/atlases/ara)
  -po P_OUTFILE, --p_outfile P_OUTFILE
                        Output filenames (default: pvalue_heatmap)

"""
   
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Help")
        self.setGeometry(100, 100, 720, 600)

        layout = QVBoxLayout(self)

        text_region = QTextEdit()
        text_region.setReadOnly(True)
        text_region.setText(self.docs_message)
        text_region.append("<b>Parameter descriptions:</b>")
        text_region.append(self.parameter_description)
        layout.addWidget(text_region)

        button = QPushButton("Close", self)
        button.clicked.connect(self.close)
        layout.addWidget(button)

    def close(self):
        self.accept()
