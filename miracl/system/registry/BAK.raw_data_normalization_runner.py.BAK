from typing import Optional, Dict
import subprocess


def raw_data_normalization_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mrdn_num_erosion": "--num_erosion",
        "--mrdn_alpha": "--alpha",
        "--mrdn_thr": "--thr",
        "--mrdn_cpu_load": "--cpu_load",
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
