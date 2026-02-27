from typing import Optional, Dict
import subprocess


def preprocessing_parallel_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mpp_cpu_load": "--cpu_load",
        "--mpp_cl_percentage": "--cl_percentage",
        "--mpp_cl_lsm_footprint": "--cl_lsm_footprint",
        "--mpp_cl_back_footprint": "--cl_back_footprint",
        "--mpp_lsm_vs_back_weight": "--lsm_vs_back_weight",
        "--mpp_deconv_bin_thr": "--deconv_bin_thr",
        "--mpp_deconv_sigma": "--deconv_sigma",
        "--mpp_save_intermediate_results_flag": "--save_intermediate_results_flag",
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
