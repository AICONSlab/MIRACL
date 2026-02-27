import shlex
from typing import List
import subprocess


def generic_runner(tokens: List[str], execute: bool = True):
    """
    The Courier. Just delivers the tokens to the OS.
    Using shell=False (default) is safer.
    """
    print(f"Executing with command: {' '.join(shlex.quote(t) for t in tokens)}")
    if execute:
        return subprocess.run(tokens, check=True)
    return tokens
