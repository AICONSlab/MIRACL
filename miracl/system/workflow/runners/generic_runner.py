"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

This is the generic default runner. The idea is that runners can easily be swapped
depending on what's required by any particular script. This will be even more useful
once we implement cloud functionality into MIRACL.
"""

import shlex
import subprocess
from typing import List
from miracl.system.logger import get_logger

logger = get_logger(__name__)


def generic_runner(tokens: List[str], execute: bool = True):
    """
    This is the default runner. It delivers the tokens to the OS. The tokens come from
    the command plan builders and are delievered to the runner by the orchestrator.
    """
    cmd_str = " ".join(shlex.quote(t) for t in tokens)
    logger.info("Runner called | execute=%s | command=%s", execute, cmd_str)

    if not execute:
        logger.info("Dry run - skipping execution | command=%s", cmd_str)
        return tokens

    try:
        logger.info("Executing command | command=%s", cmd_str)
        result = subprocess.run(tokens, check=True)
        logger.success("Command completed successfully | command=%s", cmd_str)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(
            "Command failed | returncode=%d | command=%s", e.returncode, cmd_str
        )
        raise
