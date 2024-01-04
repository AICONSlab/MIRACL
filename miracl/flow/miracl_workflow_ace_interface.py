# import re
import subprocess
import sys
import os
import logging
from pathlib import Path
from miracl.flow import miracl_workflow_ace_parser, ace_test_interface
from miracl.seg import ace_interface

# Create a logger
logger = logging.getLogger("ace_flow_interface_logger")
logger.setLevel(logging.DEBUG)

# file_handler = logging.FileHandler("debug.log")
# file_handler.setLevel(logging.WARNING)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def test_none_args(sagittal, coronal, axial, dim):
    """
    This function checks if arguments are provided for --sh_sagittal,
    --sh_coronal, --sh_axial and --sh_figure_dim and composes the
    'miracl stats heatmap_group' command accordingly. This is necessary
    because the heatmap fn requires nargs=5 for the axes and nargs=2 for
    the figure dimensions.
    """

    def arg_checker(prev_cmd, arg, arg_name, flag):
        """
        This is a nested function that performs the actual checks for
        each provided argument.
        """
        if arg is None:
            logger.debug(f"No arguments for {arg_name} provided")
        else:
            logger.debug(f"Arguments for {arg_name} provided")
            prev_cmd += f"-{flag} {' '.join(map(str, arg))} "

        return prev_cmd

    # Define base cmd to add on to
    base_cmd = "miracl stats heatmap_group "

    saggital_result = arg_checker(base_cmd, sagittal, "sagittal", "s")
    coronal_result = arg_checker(saggital_result, coronal, "coronal", "c")
    axial_result = arg_checker(coronal_result, axial, "axial", "a")
    final_result = arg_checker(axial_result, dim, "figure dimensions", "f")

    return final_result


def main():
    args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    args = args_parser.parse_args()

    miracl_home = Path(os.environ["MIRACL_HOME"])
    # flow_dir = miracl_home / "flow"

    # modified_dict = {re.sub(r'^seg_', '', key): value for key, value in args.__dict__.items()}

    # INFO: Set output folders

    # INFO: Call ACE interface -> returns path of seg_out

    ace_flow_seg_output_folder = Path(args.sa_output_folder) / "seg_final"
    ace_flow_seg_output_folder.mkdir(parents=True, exist_ok=True)
    # ace_interface.main(args=args)

    # INFO: Call conversion here
    # INFO: Set output folder

    ace_flow_conv_output_folder = Path(args.sa_output_folder) / "conv_final"
    ace_flow_conv_output_folder.mkdir(parents=True, exist_ok=True)
    conv_cmd = f"python {miracl_home}/conv/miracl_conv_convertTIFFtoNII.py \
    --folder {args.sa_input_folder} \
    --work_dir {args.sa_output_folder} \
    --down {args.ctn_down} \
    --channum {args.ctn_channum} \
    --chanprefix {args.ctn_chanprefix} \
    --channame {args.ctn_channame} \
    --outnii {args.ctn_outnii} \
    --resx {args.ctn_resx} \
    --resz {args.ctn_resz} \
    --center {' '.join(map(str, args.ctn_center))} \
    --downzdim {args.ctn_downzdim} \
    --prevdown {args.ctn_prevdown}"
    # subprocess.Popen(conv_cmd, shell=True).wait()

    # INFO: Call registration here
    # INFO: Pass args.seg_input_folder
    # INFO: Set output folder

    converted_nii_file = next(ace_flow_conv_output_folder.glob("*"))
    reg_cmd = f"{miracl_home}/reg/miracl_reg_clar-allen.sh \
    -i {converted_nii_file} \
    -r {args.sa_output_folder} \
    -o {args.rca_orient_code} \
    -m {args.rca_hemi} \
    -v {args.rca_voxel_size} \
    -l {args.rca_allen_label} \
    -a {args.rca_allen_atlas} \
    -s {args.rca_side} \
    -f {args.rca_no_mosaic_fig} \
    -b {args.rca_olfactory_bulb} \
    -p {args.rca_skip_cor} \
    -w {args.rca_warp}"
    # subprocess.Popen(reg_cmd, shell=True).wait()

    # INFO: Call voxelization
    ace_flow_vox_output_folder = Path(args.sa_output_folder) / "vox_final"
    ace_flow_vox_output_folder.mkdir(parents=True, exist_ok=True)

    # Stacking segmented tif files
    fiji_file = ace_flow_vox_output_folder / "stack_seg_tifs.ijm"
    stacked_tif = ace_flow_vox_output_folder / "stacked_seg_tif.tif"

    # Check if Fiji file already exists and delete if True
    # if fiji_file.is_file():
    #     fiji_file.unlink()
    # Check if stacked tif file already exists and delete if True
    # if stacked_tif.is_file():
    #     stacked_tif.unlink()

    # print("  Stacking segmented tifs...")
    # with open(fiji_file, "w") as file:
    #     file.write(f'File.openSequence("{ace_flow_seg_output_folder}", "virtual");\n')
    #     file.write(f'saveAs("Tiff", "{stacked_tif}");\n')
    #     file.write("close();\n")
    #
    # fiji_stack_cmd = f"Fiji \
    #         --headless \
    #         --console \
    #         -macro \
    #         {fiji_file}"
    # subprocess.Popen(fiji_stack_cmd, shell=True).wait()

    print("  voxelizing stacked tif...")
    vox_cmd = f"miracl seg voxelize \
    --seg {stacked_tif} \
    --res {args.rca_voxel_size} \
    --down {args.ctn_down}"
    # -vx {args.} \
    # -vz {args.}"
    # subprocess.Popen(vox_cmd, shell=True).wait()

    # INFO: Call warping
    ace_flow_warp_output_folder = Path(args.sa_output_folder) / "warp_final"
    ace_flow_warp_output_folder.mkdir(parents=True, exist_ok=True)
    clarity_reg_dir = Path(args.sa_output_folder) / "clar_allen_reg"
    voxelized_segmented_tif = list(
        ace_flow_vox_output_folder.glob("voxelized_seg_*.nii.gz")
    )[0]
    orientation_file = ace_flow_warp_output_folder / "ort2std.txt"

    # Check if orientation file already exists and delete if True
    # if orientation_file.is_file():
    #     orientation_file.unlink()

    # with open(orientation_file, "w") as file:
    #     file.write(f'tifdir={ace_flow_vox_output_folder}\n')
    #     file.write(f'ortcode={args.rca_orient_code}')

    print("  warping voxelized tif...")
    # print(f"warp_dir: {ace_flow_warp_output_folder}")
    # print(f"reg_dir: {clarity_reg_dir}")
    # print(f"vox_seg_tif: {voxelized_segmented_tif}")
    # print(f"orientation_file: {orientation_file}")
    warp_cmd = f"miracl reg warp_clar \
    -r {clarity_reg_dir} \
    -i {voxelized_segmented_tif} \
    -o {orientation_file} \
    -s {args.rwc_seg_channel} \
    -v {args.rca_voxel_size}"
    # subprocess.Popen(warp_cmd, shell=True).wait()

    # INFO: Call permutation cluster stats here
    ace_flow_cluster_output_folder = Path(args.sa_output_folder) / "clust_final"
    ace_flow_cluster_output_folder.mkdir(parents=True, exist_ok=True)

    # subprocess.run(["python", "miracl_workflow_ace_stats.py", "-h"], cwd=flow_dir)

    # INFO: Call heatmap stats here
    ace_flow_heatmap_output_folder = Path(args.sa_output_folder) / "heat_final"
    ace_flow_heatmap_output_folder.mkdir(parents=True, exist_ok=True)

    # Run args checks
    tested_heatmap_cmd = test_none_args(
        args.sh_sagittal, args.sh_coronal, args.sh_axial, args.sh_figure_dim
    )

    # Add remaining args to checked heatmap cmd
    tested_heatmap_cmd += f"-g1 {args.sh_group1} -g2 {args.sh_group2} -v {args.sh_vox} -gs {args.sh_sigma} -p {args.sh_percentile} -cp {args.sh_colourmap_pos} -cn {args.sh_colourmap_neg} -d {ace_flow_heatmap_output_folder} -o {args.sh_outfile} -e {args.sh_extension} --dpi {args.sh_dpi}"

    # Execute heatmap cmd
    print("  running heatmap function...")
    subprocess.Popen(tested_heatmap_cmd, shell=True).wait()

    # sys.exit()
    #
    # def run_cmd(cmd):
    #     try:
    #         result = subprocess.run(
    #             cmd, check=True, text=True, capture_output=True, shell=True
    #         )
    #         print("Command executed successfully.")
    #         print(result.stdout)
    #     except subprocess.CalledProcessError as e:
    #         print(f"Command failed with return code {e.returncode}")
    #
    # run_cmd(heatmap_cmd)


if __name__ == "__main__":
    main()
