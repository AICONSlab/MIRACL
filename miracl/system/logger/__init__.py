"""
miracl/system/logger/__init__.py
=================================
Public API for MIRACL's logging system.

This is the only module that pipeline code should ever import from.
The implementation details in ``logger_config.py`` are intentionally
kept separate so they can evolve without touching every call site.

Typical usage
-------------
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

Custom levels
-------------
Two custom levels are defined above the standard set:

    DEV (5)
        Step-by-step execution trace for active codebase exploration.
        Safe to commit and leave in code permanently — only surfaces when
        MIRACL_LOG_LEVEL=DEV is explicitly set. Invisible even at DEBUG.

    SUCCESS (25)
        Marks the clean completion of a major pipeline stage.
        Sits above INFO so it stands out, below WARNING so it implies
        nothing went wrong.

Environment variables
---------------------
See ``logger_config.py`` for the full list of environment variables
that control log level, per-module overrides, output format, and
file logging behaviour.
"""

import logging

from miracl.system.logger.logger_config import DEV, SUCCESS, setup_logging  # noqa: F401
# DEV, SUCCESS, and setup_logging are re-exported here so callers can import
# them directly from this module without knowing about logger_config:
#
#   from miracl.system.logger import get_logger, setup_logging, DEV, SUCCESS


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured for use within the MIRACL package.

    This is the single call site every MIRACL module should use to
    obtain a logger. It guarantees that logging is initialised before
    the first record is emitted, regardless of whether the caller
    remembered to call ``setup_logging()`` explicitly at startup.

    Parameters
    ----------
    name : str
        The logger's name. Always pass ``__name__`` so the dotted
        module path is used (e.g. ``"miracl.flow.ace.ace_flow"``).
        This places the logger correctly in the hierarchy and makes
        log output immediately tell you which module produced it.
        It also means per-module env var overrides like
        ``MIRACL_LOG_LEVEL_FLOW_ACE=DEBUG`` will match correctly.

    Returns
    -------
    logging.Logger
        A standard Python ``Logger`` instance with two additional methods:

        ``logger.dev(msg)``
            Emits at DEV level (5). Step-by-step execution trace.
            Only visible when MIRACL_LOG_LEVEL=DEV.

        ``logger.success(msg)``
            Emits at SUCCESS level (25). Marks clean stage completion.

        ``logging.getLogger()`` is idempotent: calling it twice with the
        same name always returns the *same* object, so there is no risk
        of creating duplicate loggers.

    Examples
    --------
    >>> from miracl.system.logger import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.dev("Affine matrix:\\n%s", affine)
    >>> logger.info("Data loaded | shape=%s", data.shape)
    >>> logger.success("Registration complete | elapsed=%.2fs", elapsed)
    """
    # Ensure logging is configured before the first record is emitted.
    # setup_logging() is idempotent — if it has already been called
    # (e.g. from a previous get_logger call or explicitly at startup),
    # this call returns immediately without changing anything.
    setup_logging()

    # logging.getLogger() is the standard library function that returns
    # the Logger for the given name, creating it if it doesn't exist yet.
    # The returned logger is fully configured via the root logger that
    # setup_logging() established — no further configuration is needed here.
    return logging.getLogger(name)
