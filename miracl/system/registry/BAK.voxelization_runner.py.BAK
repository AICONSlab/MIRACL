from typing import Optional, Dict
import subprocess


def voxelization_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mv_cpu_load": "--cpu_load",
        "--mv_downsample_yx_axis": "--downsample_yx_axis",
        "--mv_downsample_z_axis": "--downsample_z_axis",
        "--mv_method": "--method",
        "--mv_out_name": "--out_name",
        "--mv_res_xy": "--res_xy",
        "--mv_res_z": "--res_z",
    }
    parts = [script]
    for flag, value in mapping.items():
        new_flag = flag_map.get(flag, flag)  # fallback to original if no mapping
        # if value is not None:
        parts.append(f"{new_flag} {value}")
    cmd_str = " ".join(map(str, parts))
    print(f"Running: {cmd_str}")
    subprocess.run(cmd_str, shell=True)
    return cmd_str
