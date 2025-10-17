from typing import Optional, Dict
import subprocess


def conv_runner(script: str, mapping: Dict[str, Optional[str]]):
    flag_map = {
        "--mctn_down": "--down",
        "--mctn_channum": "--channum",
        "--mctn_chanprefix": "--chanprefix",
        "--mctn_channame": "--channame",
        "--mctn_outnii": "--outnii",
        "--mctn_resx": "--resx",
        "--mctn_resz": "--resz",
        "--mctn_center": "--center",
        "--mctn_downzdim": "--downzdim",
        "--mctn_prevdown": "--prevdown",
        "--mctn_percentile_thr": "--percentile_thr",
        # "--mctn_folder": "--folder",
        # "--mctn_work_dir": "--work_dir",
    }
    parts = [script]
    for flag, value in mapping.items():
        new_flag = flag_map.get(flag, flag)  # fallback to original if no mapping
        # if value is not None:
        if isinstance(value, list):
            value = " ".join(map(str, value))
        parts.append(f"{new_flag} {value}")
    cmd_str = " ".join(map(str, parts))
    print(f"Running: {cmd_str}")
    subprocess.run(cmd_str, shell=True)
    return cmd_str
