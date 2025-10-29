# miracl/system/registry/runners/generic_runner.py
import subprocess
from typing import Optional, Dict


def generic_runner(
    script: str,
    mapping: Dict[str, Optional[str]],
    *,
    flag_map=None,
    execute=False,
):
    """A configurable runner that supports optional flag mapping and execution."""
    flag_map = flag_map or {}
    parts = [script]
    for flag, value in mapping.items():
        new_flag = flag_map.get(flag, flag)
        parts.append(f"{new_flag} {value}")
    cmd_str = " ".join(map(str, parts))
    print(f"Running: {cmd_str}")
    if execute:
        subprocess.run(cmd_str, shell=True, check=True)
    return cmd_str
