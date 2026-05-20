"""
Code written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Public API for MIRACL's logging system.

This is the only module that pipeline code should ever import from. The implementation
details in logger_config.py are intentionally kept separate so they can evolve without
touching every call site.

At the top of any MIRACL module::

    from miracl.system.logger import get_logger

    logger = get_logger(__name__)

    logger.dev("Entering function | affine=\\n%s", affine_matrix)
    logger.debug("Computed voxel size | vx=%s vz=%s", vx, vz)
    logger.info("Stage complete | elapsed=%.2fs", elapsed)
    logger.success("Pipeline finished successfully")
    logger.warning("Unexpected input — proceeding with defaults")
    logger.error("Operation failed | reason=%s", err)
    logger.critical("Unrecoverable error", exc_info=True)

Two custom levels are defined above the standard set:

    DEV (5)
        Step-by-step execution trace for active codebase exploration. Safe to commit
        and leave in code permanently. Only surfaces when MIRACL_LOG_LEVEL=DEV is
        explicitly set. Invisible even at DEBUG.

    SUCCESS (25)
        Marks the clean completion of a major pipeline stage. Sits above INFO so it
        stands out, below WARNING so it implies nothing went wrong.
"""

import logging

from miracl.system.logger.logger_config import DEV, SUCCESS, setup_logging
# DEV, SUCCESS, and setup_logging are re-exported here so callers can import
# them directly from this module without knowing about logger_config:
#
#   from miracl.system.logger import get_logger, setup_logging, DEV, SUCCESS


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger configured for use within the MIRACL package.

    This is the single call site every MIRACL module should use to obtain a logger.
    It guarantees that logging is initialised before the first record is emitted,
    regardless of whether the caller remembered to call setup_logging() explicitly at
    startup.
    """
    setup_logging()

    return logging.getLogger(name)
