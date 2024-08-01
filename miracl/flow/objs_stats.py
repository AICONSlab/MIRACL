from miracl_datamodel import MiraclObj, ArgumentType
from pathlib import Path


class StatsAceObjs:
    atlas_dir = MiraclObj(
        id="3c106f75-5f4a-45b2-a151-b6e85ff62d1a",
        name="u_atlas_dir",
        tags=["ace", "stats", "ace_flow"],
        gui_label=["Path to altas dir"],
        module="ace",
        module_group="stats",
        cli_s_flag="ua",
        cli_l_flag="u_atlas_dir",
        cli_help="path of atlas directory (default: %(default)s)",
        gui_group={"ace_flow": "corr_stats"},
        version_added="2.4.0",
        # FIX: Needs to be the ARA env ref to ARA folder
        # default=500,
    )

    p_outfile = MiraclObj(
        id="3c106f75-5f4a-45b2-a151-b6e85ff62d1a",
        name="p_outfile",
        tags=["ace", "stats", "ace_flow"],
        gui_label=["Output filename"],
        module="ace",
        cli_obj_type=ArgumentType.STRING,
        module_group="stats",
        cli_s_flag="po",
        cli_l_flag="p_outfile",
        cli_help="path of atlas directory (default: %(default)s)",
        gui_group={"ace_flow": "corr_stats"},
        version_added="2.4.0",
        obj_default="pvalue_heatmap",
    )


class StatsAceClustObjs:
    atlas_dir = MiraclObj(
        id="e7824ae1-af2d-4d51-8322-2ade4cf68379",
        name="pcs_atlas_dir",
        tags=["ace", "stats", "cluserwise", "ace_flow"],
        cli_s_flag="pcsa",
        cli_l_flag="pcs_atlas_dir",
        cli_help="path of atlas directory",
        gui_label=["Path to atlas dir"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default="miracl_home",
        module="ace",
        module_group="stats",
    )

    num_perm = MiraclObj(
        id="4c6a1223-4347-4634-a3b0-475967a967f0",
        name="pcs_num_perm",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsn",
        cli_l_flag="pcs_num_perm",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="number of permutations (default: %(default)s)",
        gui_group={"ace_flow": "clust"},
        gui_label=["# permutations"],
        version_added="2.4.0",
        obj_default=500,
        module="ace",
        module_group="stats",
    )

    img_resolution = MiraclObj(
        id="5978055a-6c10-49d1-8b6f-c531f9b92d63",
        name="pcs_img_resolution",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsr",
        cli_l_flag="pcs_img_resolution",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="resolution of images in um (default: %(default)s)",
        gui_group={"ace_flow": "clust"},
        gui_label=["Resolution of images (um)"],
        version_added="2.4.0",
        cli_choices=[10, 25, 50],
        obj_default=25,
        module="ace",
        module_group="stats",
    )

    smoothing_fwhm = MiraclObj(
        id="b84ab2a5-27e5-429d-a015-a8df2335271b",
        name="pcs_smoothing_fwhm",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsfwhm",
        cli_l_flag="pcs_smoothing_fwhm",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="fwhm of Gaussian kernel in pixel (default: %(default)s)",
        gui_label=["fwhm of Gaussian kernel (px)"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default=3,
        module="ace",
        module_group="stats",
    )

    tfce_start = MiraclObj(
        id="95bbc02a-1d5b-4b66-87c3-fe54c735aa18",
        name="pcs_tfce_start",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsstart",
        cli_l_flag="pcs_tfce_start",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="tfce threshold start (default: %(default)s)",
        gui_label=["tfce threshold start"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default=0.01,
        module="ace",
        module_group="stats",
    )

    tfce_step = MiraclObj(
        id="9c282d72-bf43-4d15-9da2-11cf64e605de",
        name="pcs_tfce_step",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsstep",
        cli_l_flag="pcs_tfce_step",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="tfce threshold step (default: %(default)s)",
        gui_label=["tfce threshold step"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default=5,
        module="ace",
        module_group="stats",
    )

    cpu_load = MiraclObj(
        id="86dcfae0-b98b-4523-aaac-41b60529a31a",
        name="pcs_cpu_load",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsc",
        cli_l_flag="pcs_cpu_load",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="Percent of cpus used for parallelization (default: %(default)s)",
        gui_label=["% CPU's for parallelization"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default=0.9,
        module="ace",
        module_group="stats",
    )

    tfce_h = MiraclObj(
        id="5237ff1a-4cbb-4cb9-ab38-2fb2a23131b2",
        name="pcs_tfce_h",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsh",
        cli_l_flag="pcs_tfce_h",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="tfce H power (default: %(default)s)",
        gui_label=["tfce H power"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default=2,
        module="ace",
        module_group="stats",
    )

    tfce_e = MiraclObj(
        id="54dfc9df-0d3d-4b93-920f-40f70365a881",
        name="pcs_tfce_e",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcse",
        cli_l_flag="pcs_tfce_e",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="tfce E power (default: %(default)s)",
        gui_label=["tfce E power"],
        gui_group={"ace_flow": "clust"},
        version_added="2.4.0",
        obj_default=0.5,
        module="ace",
        module_group="stats",
    )

    step_down_p = MiraclObj(
        id="85596967-b0ce-41a8-b4b3-676a3281e607",
        name="pcs_step_down_p",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcssp",
        cli_l_flag="pcs_step_down_p",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="step down p-value (default: %(default)s)",
        gui_group={"ace_flow": "clust"},
        gui_label=["Step down p-value"],
        version_added="2.4.0",
        obj_default=0.3,
        module="ace",
        module_group="stats",
        range_formatting_vals={
            "min_val": 0.0000,
            "max_val": 1.0000,
            "increment_val": 0.01,
            "nr_decimals": 4,
        },
    )

    mask_thr = MiraclObj(
        id="bfddb1db-0d53-4908-877a-2f6c87d8024e",
        name="pcs_mask_thr",
        tags=["ace", "stats", "clusterwise", "ace_flow"],
        cli_s_flag="pcsm",
        cli_l_flag="pcs_mask_thr",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="percentile to be used for binarizing difference of the mean (default: %(default)s)",
        gui_group={"ace_flow": "clust"},
        gui_label=["% for binarizing mean diff"],
        version_added="2.4.0",
        obj_default=95,
        module="ace",
        module_group="stats",
        range_formatting_vals={
            "min_val": 0,
            "max_val": 100,
            "increment_val": 1,
        },
    )


class StatsAceCorrObjs:
    pvalue_thr = MiraclObj(
        id="c0cf81cb-8ad1-4982-974b-a5b2e589d6d1",
        name="cf_pvalue_thr",
        tags=["ace", "stats", "correlation", "ace_flow"],
        cli_s_flag="cft",
        cli_l_flag="cf_pvalue_thr",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold for binarizing p value (default: %(default)s)",
        gui_group={"ace_flow": "corr_stats"},
        gui_label=["Threshold binarizing p-value"],
        version_added="2.4.0",
        obj_default=0.05,
        module="ace",
        module_group="stats",
        range_formatting_vals={
            "min_val": 0.0000,
            "max_val": 1.0000,
            "increment_val": 0.01,
            "nr_decimals": 4,
        },
    )


class StatsHeatmapObjs:
    group1 = MiraclObj(
        id="3a7bc2f7-2eb8-45aa-aa32-0d11762b7565",
        name="sh_group1",
        tags=["heatmap", "stats", "ace_flow"],
        cli_s_flag="shg1",
        cli_l_flag="sh_group1",
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to group 1 directory",
        gui_label=["Path to group 1 dir"],
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default=None,
        module="heatmap_group",
        module_group="stats",
    )

    group2 = MiraclObj(
        id="8e0ef0a5-419c-48b4-9d11-e61aa9e69297",
        name="sh_group2",
        tags=["heatmap", "stats", "ace_flow"],
        cli_s_flag="shg2",
        cli_l_flag="sh_group2",
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to group 2 directory",
        gui_group={"ace_flow": "heatmap"},
        gui_label=["Path to group 1 dir"],
        version_added="2.4.0",
        module="heatmap_group",
        module_group="stats",
        obj_default=None,
    )

    vox = MiraclObj(
        id="68cc3699-25a4-4b28-9407-9c22c6a2b880",
        name="sh_vox",
        tags=["heatmap", "stats", "ace_flow"],
        cli_s_flag="shv",
        cli_l_flag="sh_vox",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="voxel size/Resolution in um",
        gui_group={"ace_flow": "heatmap"},
        gui_label=["Voxel size (um)"],
        version_added="2.4.0",
        cli_choices=[10, 25, 50],
        module="heatmap_group",
        module_group="stats",
        obj_default=25,
    )

    sigma = MiraclObj(
        id="a8578f34-5f92-4788-8eb9-3f39c8279dd8",
        name="sh_sigma",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Guassian smoothing sigma"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shgs",
        cli_l_flag="sh_sigma",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Gaussian smoothing sigma (default: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default=4,
        range_formatting_vals={
            "min_val": 0,
            "max_val": 1000,
            "increment_val": 1,
        },
    )

    percentile = MiraclObj(
        id="dcb8da8a-1a45-4e33-8489-5acc71049c3b",
        name="sh_percentile",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["% threshold svg"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shp",
        cli_l_flag="sh_percentile",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="percentile (%%) threshold for registration-to-input data check svg animation (default: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default=10,
        range_formatting_vals={
            "min_val": 0,
            "max_val": 100,
            "increment_val": 1,
        },
    )

    colourmap_pos = MiraclObj(
        id="55fba010-fcf3-4aab-95ca-6dcd1891f3a4",
        name="sh_colourmap_pos",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Matplotlib colourmap pos values"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shcp",
        cli_l_flag="sh_colourmap_pos",
        cli_obj_type=ArgumentType.STRING,
        cli_help="matplotlib colourmap for positive values (default: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default="Reds",
    )

    colourmap_neg = MiraclObj(
        id="b462edc4-bd58-44a8-9a26-25d786f17dcd",
        name="sh_colourmap_neg",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Matplotlib colourmap neg values"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shcn",
        cli_l_flag="sh_colourmap_neg",
        cli_obj_type=ArgumentType.STRING,
        cli_help="matplotlib colourmap for negative values (default: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default="Blues",
    )

    sagittal = MiraclObj(
        id="6de23309-e0d4-43dd-aa7b-317e566d4cf8",
        name="sh_sagittal",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Slicing across sagittal axis"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shs",
        cli_l_flag="sh_sagittal",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="slicing across sagittal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        cli_nargs=5,
        obj_default=None,
    )

    coronal = MiraclObj(
        id="01d626c7-ba22-4b32-a49a-dbcf2d1b249a",
        name="sh_coronal",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Slicing across coronal axis"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shc",
        cli_l_flag="sh_coronal",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        cli_nargs=5,
    )

    axial = MiraclObj(
        id="b30c0ced-4a0d-48a2-9ff5-49cd3c59bf66",
        name="sh_axial",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Slicing across axial axis"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="sha",
        cli_l_flag="sh_axial",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        cli_nargs=5,
    )

    figure_dim = MiraclObj(
        id="b8405406-07e7-45bc-929a-87d480e9c91e",
        name="sh_figure_dim",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Figure dimensions"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shf",
        cli_l_flag="sh_figure_dim",
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="figure width and height",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        cli_nargs=2,
        obj_default=None,
    )

    outfolder = MiraclObj(
        id="650a0bdf-d7f2-4f97-8e24-2854bb21a403",
        name="sh_dir_outfile",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Output folder"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shd",
        cli_l_flag="sh_dir_outfile",
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output file directory (default is cwd: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default=Path.cwd(),
    )

    outfile = MiraclObj(
        id="2a74cd39-83d2-4e69-b326-3ad36d8d1034",
        name="sh_outfile",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Output filenames"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="sho",
        cli_l_flag="sh_outfile",
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output filenames (default: group_1 group_2 group_difference)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        cli_nargs="+",
        obj_default=["group_1", "group_2", "group_difference"],
    )

    extension = MiraclObj(
        id="8ec70813-f78b-444a-9431-36c58435aa2c",
        name="sh_extension",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Heatmap fig extension"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="she",
        cli_l_flag="sh_extension",
        cli_obj_type=ArgumentType.STRING,
        cli_help="heatmap figure extension (default: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default="tiff",
    )

    dpi = MiraclObj(
        id="885d3bcc-6dd9-41ad-ac09-b52272da275f",
        name="sh_dpi",
        tags=["heatmap", "stats", "ace_flow"],
        gui_label=["Dots per inch (dpi)"],
        module="heatmap_group",
        module_group="stats",
        cli_s_flag="shdpi",
        cli_l_flag="sh_dpi",
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="dots per inch (default: %(default)s)",
        gui_group={"ace_flow": "heatmap"},
        version_added="2.4.0",
        obj_default=500,
    )
