from typing import Optional, Dict
import subprocess


def inference_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mi_binarization_threshold": "--binarization_threshold",
        "--mi_tissue_percentage_threshold": "--tissue_percentage_threshold",
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
