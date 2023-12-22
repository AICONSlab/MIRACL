# import re
import subprocess
import os
from pathlib import Path
from miracl.flow import miracl_workflow_ace_parser, ace_test_interface
from miracl.seg import ace_interface


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
    ace_interface.main(args=args)

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
    subprocess.Popen(conv_cmd, shell=True).wait()

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
    subprocess.Popen(reg_cmd, shell=True).wait()

    # INFO: Call voxelization
    ace_flow_vox_output_folder = Path(args.sa_output_folder) / "vox_final"
    ace_flow_vox_output_folder.mkdir(parents=True, exist_ok=True)

    # Stacking segmented tif files
    fiji_file = ace_flow_vox_output_folder / "stack_seg_tifs.ijm"
    stacked_tif = ace_flow_vox_output_folder / "stacked_seg_tif.tif"

    # Check if Fiji file already exists and delete if True
    if fiji_file.is_file():
        fiji_file.unlink()
    # Check if stacked tif file already exists and delete if True
    if stacked_tif.is_file():
        stacked_tif.unlink()

    print("  Stacking segmented tifs...")
    with open(fiji_file, "w") as file:
        file.write(f'File.openSequence("{ace_flow_seg_output_folder}", "virtual");\n')
        file.write(f'saveAs("Tiff", "{stacked_tif}");\n')
        file.write("close();\n")

    fiji_stack_cmd = f"Fiji \
            --headless \
            --console \
            -macro \
            {fiji_file}"
    subprocess.Popen(fiji_stack_cmd, shell=True).wait()

    vox_cmd = f"miracl seg voxelize \
    --seg {stacked_tif} \
    --res {args.rca_voxel_size} \
    --down {args.ctn_down}"
    # -vx {args.} \
    # -vz {args.}"
    subprocess.Popen(vox_cmd, shell=True).wait()

    # INFO: Call warping
    ace_flow_warp_output_folder = Path(args.sa_output_folder) / "warp_final"
    ace_flow_warp_output_folder.mkdir(parents=True, exist_ok=True)
    clarity_reg_dir = Path(args.sa_output_folder) / "clar_allen_reg"
    voxelized_segmented_tif = list(ace_flow_vox_output_folder.glob("voxelized_seg_*.nii.gz"))[0]
    orientation_file = ace_flow_warp_output_folder / "ort2std.txt"

    # Check if orientation file already exists and delete if True
    if orientation_file.is_file():
        orientation_file.unlink()

    with open(orientation_file, "w") as file:
        file.write(f'tifdir={ace_flow_vox_output_folder}\n')
        file.write(f'ortcode={args.rca_orient_code}')

    print(f"warp_dir: {ace_flow_warp_output_folder}")
    print(f"reg_dir: {clarity_reg_dir}")
    print(f"vox_seg_tif: {voxelized_segmented_tif}")
    print(f"orientation_file: {orientation_file}")
    warp_cmd = f"miracl reg warp_clar \
    -r {clarity_reg_dir} \
    -i {voxelized_segmented_tif} \
    -o {orientation_file} \
    -s {args.rwc_seg_channel} \
    -v {args.rca_voxel_size}"
    subprocess.Popen(warp_cmd, shell=True).wait()

    # INFO: Call permutation cluster stats

    # subprocess.run(["python", "miracl_workflow_ace_stats.py", "-h"], cwd=flow_dir)


if __name__ == "__main__":
    main()
