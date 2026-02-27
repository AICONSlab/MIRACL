from typing import Optional, Dict


def default_runner(script: str, mapping: Dict[str, Optional[str]]):
    parts = [script]
    for flag, value in mapping.items():
        # if value is not None:
        parts.append(f"{flag} {value}")
    cmd_str = " ".join(map(str, parts))
    print(f"Running: {cmd_str}")
    # subprocess.run(cmd_str, shell=True)
    return cmd_str
