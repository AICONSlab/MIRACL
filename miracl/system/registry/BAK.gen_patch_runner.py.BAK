from typing import Optional, Dict
import subprocess


def gen_patch_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mgp_cpu_load": "--cpu_load",
        "--mgp_patch_size": "--patch_size",
        "--mgp_brain_mask_erosion_flag": "--brain_mask_erosion_flag",
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
