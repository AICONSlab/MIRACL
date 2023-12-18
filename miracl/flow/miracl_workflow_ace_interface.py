# import re
import subprocess
import sys
import os
from pathlib import Path
from miracl.flow import miracl_workflow_ace_parser, ace_test_interface
from miracl.seg import ace_interface


def main():
    args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    args = args_parser.parse_args()

    miracl_home = Path(os.environ["MIRACL_HOME"])
    flow_dir = miracl_home / "flow"

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
    # conv_cmd = f"python {miracl_home}/conv/miracl_conv_convertTIFFtoNII.py \
    # --folder {args.sa_input_folder} \
    # --work_dir {args.sa_output_folder} \
    # --down {args.ctn_down} \
    # --channum {args.ctn_channum} \
    # --chanprefix {args.ctn_chanprefix} \
    # --channame {args.ctn_channame} \
    # --outnii {args.ctn_outnii} \
    # --resx {args.ctn_resx} \
    # --resz {args.ctn_resz} \
    # --center {' '.join(map(str, args.ctn_center))} \
    # --downzdim {args.ctn_downzdim} \
    # --prevdown {args.ctn_prevdown}"
    # subprocess.Popen(conv_cmd, shell=True).wait()

    # INFO: Call registration here
    # INFO: Pass args.seg_input_folder
    # INFO: Set output folder

    # FIX: Add args.rca_voxel_size to voxelization parser
    converted_nii_file = next(ace_flow_conv_output_folder.glob('*'))
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
    vox_cmd = "miracl seg voxelize \
    --seg {args.}\
    --res {args.rca_voxel_size}\
    --down {args.}"
    subprocess.Popen(vox_cmd, shell=True).wait()

    # INFO: Call warping
    warp_cmd = "miracl reg warp_clar \
    -r {args.rwc}\
    -i {args.rwc}\
    -o {args.rwc}\
    -s {args.rwc_seg_chanell}"
    subprocess.Popen(warp_cmd, shell=True).wait()

    # INFO: Call permutation cluster stats

    # subprocess.run(["python", "miracl_workflow_ace_stats.py", "-h"], cwd=flow_dir)


if __name__ == "__main__":
    main()
