"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Part of the MIRACL runtime module. This will become more important once verbose help
functionality is implemented. This is the base module for environment configuration and
must be the first thing called at any MIRACL entry point! Before any other MIRACL
modules are imported!!

Since the configuration needs to be initialized before the rest of the MIRACL system,
including the logger infra, we are keeping this in its own file as to not accidentally
trigger a premature import anywhere else in the system.

What I mention above about the verbose help feature refers to adding more pre-import
stuff here as the feature grows. For example suppressing optional args. Everything
else will inherit from this.
"""

import sys
import os
import logging


def configure_runtime():
    """
    Bootstraps the Miracl environment before core modules are imported. Disables file
    logging if the user is invoking help. Without this, the help would alwyas be
    preceded by a logging message. Just a bit less noisy.

    Again, and I can't stress this enough, this function must be called at the top of
    every MIRACL entry point, before any other MIRACL imports!!

    Returns:
        None: All effects are applied to process-global state.
    """
    is_help = "-h" in sys.argv or "--help" in sys.argv

    if is_help:
        logging.disable(
            logging.CRITICAL
        )  # Raises global logging threshold above CRITICAL
        os.environ["MIRACL_LOG_TO_FILE"] = (
            "false"  # Suppress opening or creating log file
        )
