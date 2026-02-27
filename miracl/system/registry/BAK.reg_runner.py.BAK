from typing import Optional, Dict
import subprocess


def reg_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mrca_orient_code": "-o",
        "--mrca_voxel_size": "-v",
        "--mrca_hemi": "-m",
        "--mrca_allen_label": "-l",
        "--mrca_allen_atlas": "-a",
        "--mrca_side": "-s",
        "--mrca_no_mosaic_fig": "-f",
        "--mrca_olfactory_bulb": "-b",
        "--mrca_skip_cor": "-p",
        "--mrca_warp": "-w",
        # "--mrca_tiff_input": "-c",
        # "--mrca_input": "-i",
        # "--mrca_output": "-r",
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
