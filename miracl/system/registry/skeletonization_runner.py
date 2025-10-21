from typing import Optional, Dict
import subprocess


def skeletonization_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--ms_threshold": "--threshold",
        "--ms_num_erosion": "--num_erosion",
        "--ms_remove_small_obj_thr": "--remove_small_obj_thr",
        "--ms_remove_large_obj_thr": "--remove_large_obj_thr",
        "--ms_elongation_thr": "--elongation_thr",
        "--ms_euler_number_thr": "--euler_number_thr",
        "--ms_cpu_load": "--cpu_load",
        "--ms_dilate_distance_transform_flag": "--dilate_distance_transform_flag",
        "--ms_alpha": "--alpha",
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
