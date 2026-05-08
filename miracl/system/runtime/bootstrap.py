"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Part of the MIRACL runtime. This will become more important once I implement the
verbose help functionality. This is kind of the base module for parsing.
"""

import sys
import os
import logging


def configure_runtime():
    """
    Bootstraps the Miracl environment before core modules are imported. Disables file
    logging if the user is invoking help.
    """
    is_help = "-h" in sys.argv or "--help" in sys.argv

    if is_help:
        logging.disable(logging.CRITICAL)
        os.environ["MIRACL_LOG_TO_FILE"] = "false"
