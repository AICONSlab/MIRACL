"""
logger_config.py
================
Central logging configuration for the MIRACL pipeline.

This module is the single source of truth for how logging is set up across
the entire application. It should never be imported directly by pipeline
modules — those should use `get_logger()` from `__init__.py` instead.

Design decisions
----------------
- Configuration is done once via `dictConfig`, which is declarative and
  easier to reason about than imperative handler/formatter construction.
- The idempotency guard (`_logging_initialized`) ensures that importing
  this module from many places never causes duplicate log output.
- Log level, file logging, and per-module overrides are driven by
  environment variables so that operators can change verbosity without
  modifying source code. This is especially useful in containerised
  (Docker/Singularity) runs which are the main usecase of MIRACL currently.
- Third-party libraries are silenced at the named-logger level rather than
  by filtering on the root, so MIRACL's own DEBUG output is unaffected.
- File logging is enabled by default and writes to a central log directory.
  Each run produces a uniquely named file (<script>_<timestamp>.log) so
  logs from different runs never overwrite each other.
- The console and file handlers use independent level thresholds:
      MIRACL_LOG_LEVEL         → root gate; controls what reaches the file
      MIRACL_CONSOLE_LOG_LEVEL → console gate; defaults to INFO regardless
                                  of what MIRACL_LOG_LEVEL is set to
  This means setting MIRACL_LOG_LEVEL=DEBUG captures a full DEBUG trace in
  the log file while keeping the terminal clean at INFO. See the environment
  variable documentation below for the interaction rules.
- The console uses a minimal formatter by default ("LEVEL: message") while
  the log file always uses the full verbose format with timestamps.
- When MIRACL_LOG_LEVEL=DEV, a dedicated "dev" formatter is used that
  includes source filename and line number, and logs are written to a
  separate "dev/" subdirectory.

Environment variables
---------------------
MIRACL_LOG_LEVEL
    Global log level. Acts as the absolute floor for the entire application -
    no record below this threshold is processed by any handler.
    Accepted values: DEV, DEBUG, INFO, WARNING, ERROR, CRITICAL (case-insensitive).
    Default: INFO

    Relationship with MIRACL_CONSOLE_LOG_LEVEL:
    MIRACL_LOG_LEVEL sets the root logger gate. MIRACL_CONSOLE_LOG_LEVEL can
    only raise the console threshold above it — it cannot lower it below.

    Examples:
        MIRACL_LOG_LEVEL=DEBUG, MIRACL_CONSOLE_LOG_LEVEL=INFO (default)
            → file receives DEBUG+, console shows INFO+ only

        MIRACL_LOG_LEVEL=DEBUG, MIRACL_CONSOLE_LOG_LEVEL=DEBUG
            → both file and console receive DEBUG+

        MIRACL_LOG_LEVEL=INFO, MIRACL_CONSOLE_LOG_LEVEL=DEBUG
            → both receive INFO+ only (root gate blocks DEBUG before it
              can reach either handler; console level is irrelevant here)

MIRACL_CONSOLE_LOG_LEVEL
    Level threshold for the console handler specifically.
    Defaults to INFO so the terminal stays clean even when MIRACL_LOG_LEVEL
    is set to DEBUG or DEV for file capture purposes.
    Accepted values: same as MIRACL_LOG_LEVEL.
    Default: INFO

MIRACL_LOG_LEVEL_<MODULE>
    Per-module override. The suffix is translated into a dotted Python module
    path by lower-casing and replacing underscores with dots, then prepending
    "miracl.".

    Examples:
        MIRACL_LOG_LEVEL_FLOW_ACE=DEBUG
            → sets "miracl.flow.ace" to DEBUG

        MIRACL_LOG_LEVEL_SEG=WARNING
            → sets "miracl.seg" to WARNING

MIRACL_LOG_FORMAT
    Console output format. Valid values: "minimal" (default), "verbose", "json", "dev".
    "minimal"  — LEVEL: message                       (default, clean terminal output)
    "verbose"  — timestamp | LEVEL | logger | message (same as the log file)
    "json"     — single-line JSON object              (containers / log aggregators)
    "dev"      — set automatically when MIRACL_LOG_LEVEL=DEV; adds file + line number

MIRACL_LOG_TO_FILE
    Set to "false" to disable file logging entirely.
    Useful in unit tests or environments where the runtime captures stdout.
    Default: "true" (file logging is on).

MIRACL_LOG_DIR
    Directory where log files are written.
    Normal runs:  <LOG_DIR>/          e.g. ~/.miracl/logs/ace_flow_20250301.log
    DEV runs:     <LOG_DIR>/dev/      e.g. ~/.miracl/logs/dev/ace_flow_20250301.log
    Default: ~/.miracl/logs
"""

import logging
import logging.config
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


# ---------------------------------------------------------------------------
# Custom log level: DEV
# ---------------------------------------------------------------------------
# DEV sits at level 5, below all standard levels:
#
#   DEV      =  5 <- step-by-step execution trace for active codebase exploration
#   DEBUG    = 10 <- internal state, parameters, computed values
#   INFO     = 20 <- user-facing progress
#   SUCCESS  = 25 <- pipeline stage completed cleanly  (defined below)
#   WARNING  = 30 <- unexpected but recoverable
#   ERROR    = 40 <- operation failed
#   CRITICAL = 50 <- unrecoverable
#
# DEV is intended for a developer who is unfamiliar with the codebase and
# wants to understand execution flow at a granular level — intermediate
# variable states, control flow decisions, loop iterations, data shapes
# at every transformation step, and so on.
#
# Key property: logger.dev() calls are safe to commit and leave in the
# codebase permanently. They will never appear unless MIRACL_LOG_LEVEL=DEV
# is explicitly set — even MIRACL_LOG_LEVEL=DEBUG will not surface them.

DEV: int = 5
logging.addLevelName(DEV, "DEV")


def _dev(self: logging.Logger, message: str, *args, **kwargs) -> None:
    """Emit a log record at the custom DEV level (5).

    Bound to ``logging.Logger`` instances so callers can write:
        logger.dev("Loop iteration | i=%d val=%s", i, val)

    Intended for step-by-step execution traces during active codebase
    exploration. Never appears unless MIRACL_LOG_LEVEL=DEV is explicitly
    set — invisible even at MIRACL_LOG_LEVEL=DEBUG.

    The ``isEnabledFor`` check short-circuits before any string formatting
    occurs, so leaving ``logger.dev()`` calls in hot loops has negligible
    runtime cost during normal operation.
    """
    if self.isEnabledFor(DEV):
        self._log(DEV, message, args, **kwargs)


logging.Logger.dev = _dev  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Custom log level: SUCCESS
# ---------------------------------------------------------------------------
# SUCCESS sits at 25 — above INFO so it isn't drowned out, but below WARNING
# so it doesn't imply anything went wrong. Used to mark the clean completion
# of a major pipeline stage (e.g. registration, segmentation).

SUCCESS: int = 25
logging.addLevelName(SUCCESS, "SUCCESS")


def _success(self: logging.Logger, message: str, *args, **kwargs) -> None:
    """Emit a log record at the custom SUCCESS level (25).

    Bound to ``logging.Logger`` instances so callers can write:
        logger.success("Registration complete | elapsed=4.2s")
    """
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


logging.Logger.success = _success  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Process-wide initialisation guard
# ---------------------------------------------------------------------------
# Python's import system caches modules after the first import, so this
# variable persists for the lifetime of the process. Every call to
# `setup_logging()` checks it first. Without this guard, importing
# `get_logger` from N modules would call `dictConfig` N times, which
# adds duplicate handlers and produces N copies of every log line.

_logging_initialized: bool = False


# ---------------------------------------------------------------------------
# Log level constants
# ---------------------------------------------------------------------------
# Both are read once at import time. Changing the environment variables after
# the module has been imported has no effect.

LOG_LEVEL: str = os.getenv(
    "MIRACL_LOG_LEVEL",
    "DEBUG",
).upper()
# `.upper()` normalises so "debug", "DEBUG", and "Debug" are all accepted.

# Independent level for the console handler:
# Defaults to INFO so the terminal stays clean even when MIRACL_LOG_LEVEL=DEBUG
# is set to capture a full trace in the log file. Operators can explicitly
# lower this to DEBUG or DEV if they also want verbose console output,
# but the root logger gate (LOG_LEVEL) still acts as the absolute floor —
# setting MIRACL_CONSOLE_LOG_LEVEL=DEBUG has no effect if MIRACL_LOG_LEVEL=INFO
# because DEBUG records never reach the console handler in the first place.
CONSOLE_LOG_LEVEL: str = os.getenv(
    "MIRACL_CONSOLE_LOG_LEVEL",
    "INFO",
).upper()


# ---------------------------------------------------------------------------
# Console formatter selection
# ---------------------------------------------------------------------------
# Maps the MIRACL_LOG_FORMAT env var value to a formatter name defined in
# the "formatters" dict inside setup_logging().
#
# To add a new formatter:
#   1. Define it in the `formatters` dict inside setup_logging().
#   2. Add its env var key -> formatter name entry here.
#   The selection logic in setup_logging() never needs to change.

FORMATTER_MAP: Dict[str, str] = {
    "minimal": "console_minimal",  # default: "LEVEL: message"
    "verbose": "standard",  # opt-in: full timestamp format
    "json": "json",  # structured output for aggregators
    "dev": "dev",  # auto-set in DEV mode; adds file+lineno
    # "colored": "colored",         # example: add new formatters here
}


# ---------------------------------------------------------------------------
# File logging configuration
# ---------------------------------------------------------------------------

FILE_LOGGING_ENABLED: bool = os.getenv("MIRACL_LOG_TO_FILE", "true").lower() != "false"

LOG_DIR: Path = Path(os.getenv("MIRACL_LOG_DIR", "/code/miracl/logs")).expanduser()


def _build_log_path(dev_mode: bool = False) -> Path:
    """Derive a timestamped log file path from the invoking script's name.

    The filename format is:  <script_stem>_<YYYYMMDD_HHMMSS>.log
    For example:             ace_flow_20250301_142201.log

    When ``dev_mode`` is True, the file is placed in a ``dev/`` subdirectory
    of LOG_DIR so DEV traces are isolated from normal run logs:
        Normal:  ~/.miracl/logs/ace_flow_20250301_142201.log
        DEV:     ~/.miracl/logs/dev/ace_flow_20250301_142201.log

    Falls back to "miracl_<timestamp>.log" when __main__.__file__ is
    unavailable (interactive shell, pytest, etc.).

    Parameters
    ----------
    dev_mode : bool
        When True, write into the dev/ subdirectory of LOG_DIR.

    Returns
    -------
    Path
        Absolute path to the log file for this run.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        main_module = sys.modules.get("__main__")
        script_stem = Path(main_module.__file__).stem
    except (AttributeError, TypeError):
        script_stem = "miracl"

    parent = LOG_DIR / "dev" if dev_mode else LOG_DIR
    return parent / f"{script_stem}_{timestamp}.log"


# ---------------------------------------------------------------------------
# Per-module override builder
# ---------------------------------------------------------------------------


def _module_overrides() -> dict:
    """Scan environment variables and build per-module logger config entries.

    Iterates over every environment variable in the current process. Any
    variable whose name starts with ``MIRACL_LOG_LEVEL_`` is treated as a
    per-module override. The suffix after the prefix is translated into a
    dotted Python module path and used as a named logger key in the
    ``dictConfig`` schema.

    Translation rules
    -----------------
    1. Strip the ``MIRACL_LOG_LEVEL_`` prefix.
    2. Lower-case the remainder.
    3. Replace ``_`` with ``.`` (env var names cannot contain dots).
    4. Prepend ``miracl.`` to anchor the path within the package.

    ``propagate: True`` is essential — without it the override logger would
    swallow records silently instead of forwarding them to the root handler.

    Returns
    -------
    dict
        Mapping of dotted logger names to their config dicts.
        Empty dict if no matching environment variables are set.

    Examples
    --------
    With ``MIRACL_LOG_LEVEL_FLOW_ACE=DEBUG`` set::

        {
            "miracl.flow.ace": {
                "level": "DEBUG",
                "propagate": True,
            }
        }
    """
    overrides: dict = {}
    prefix: str = "MIRACL_LOG_LEVEL_"

    for key, val in os.environ.items():
        if not key.startswith(prefix):
            continue

        # Strip prefix → e.g. "FLOW_ACE"
        # Lower-case  → e.g. "flow_ace"
        # Replace _   → e.g. "flow.ace"
        # Prepend pkg → e.g. "miracl.flow.ace"
        module_path = "miracl." + key[len(prefix) :].lower().replace("_", ".")

        overrides[module_path] = {
            "level": val.upper(),
            "propagate": True,
        }

    return overrides


# ---------------------------------------------------------------------------
# JSON formatter (optional, enabled via MIRACL_LOG_FORMAT=json)
# ---------------------------------------------------------------------------


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object.

    Useful when MIRACL runs inside a container and logs are shipped to an
    aggregator that can parse structured fields. Enable by setting
    ``MIRACL_LOG_FORMAT=json`` in the environment.

    Fields emitted
    --------------
    timestamp : str
        ISO 8601 datetime, e.g. "2025-03-01T14:22:01".
    level : str
        Log level name, e.g. "INFO", "SUCCESS", "DEV", "ERROR".
    logger : str
        Dotted logger name, e.g. "miracl.flow.ace.ace_flow".
    module : str
        Python module filename without extension.
    message : str
        The final formatted message string.
    exception : list[str], optional
        Only present when the record carries exception info.
    """

    def format(self, record: logging.LogRecord) -> str:
        import json
        import traceback

        payload: dict = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = traceback.format_exception(*record.exc_info)

        return json.dumps(payload)


# ---------------------------------------------------------------------------
# Main setup function
# ---------------------------------------------------------------------------


def setup_logging() -> None:
    """Configure the root logger and all handlers for the MIRACL application.

    This function is idempotent i.e. it is safe to call from multiple modules
    and will only apply configuration on the very first call. Subsequent
    calls return immediately without modifying the logging state.

    Level interaction summary
    -------------------------
    Two env vars independently control what each destination sees:

        MIRACL_LOG_LEVEL         (default: INFO)
            Root logger gate. The absolute floor — no record below this
            threshold is processed by any handler anywhere.

        MIRACL_CONSOLE_LOG_LEVEL (default: INFO)
            Console handler gate. Can only raise the console threshold
            above MIRACL_LOG_LEVEL, never lower it below.

    Typical usage patterns:

        # Default — both console and file show INFO+
        python -m miracl.flow.ace.ace_flow

        # Capture full DEBUG trace in the file, keep console at INFO
        MIRACL_LOG_LEVEL=DEBUG python -m miracl.flow.ace.ace_flow

        # Capture full DEBUG trace in both file and console
        MIRACL_LOG_LEVEL=DEBUG MIRACL_CONSOLE_LOG_LEVEL=DEBUG \\
            python -m miracl.flow.ace.ace_flow

        # Full DEV trace in file and console (auto-enables dev formatter)
        MIRACL_LOG_LEVEL=DEV python -m miracl.flow.ace.ace_flow

    Console vs file formatting
    --------------------------
        Console (stdout) — minimal by default:
            INFO: Data loaded | shape=(512, 512, 256)

        Log file — always verbose:
            2025-03-01T14:22:01 | INFO | miracl.flow.ace | Data loaded | ...

    Notes
    -----
    The ``disable_existing_loggers: False`` setting in ``dictConfig`` is
    critical. The default (``True``) silently disables any logger that was
    created before this function runs — a common trap with third-party
    libraries that instantiate loggers at import time.
    """
    global _logging_initialized

    if _logging_initialized:
        return

    # ------------------------------------------------------------------
    # Determine whether we are in DEV mode
    # ------------------------------------------------------------------
    # DEV mode affects three things:
    #   1. Active console formatter → "dev" (adds filename + line number)
    #   2. Log file location        → LOG_DIR/dev/ subdirectory
    #   3. File handler floor       → 1, so level-5 DEV records pass through

    dev_mode: bool = LOG_LEVEL == "DEV"

    # ------------------------------------------------------------------
    # Determine active console formatter
    # ------------------------------------------------------------------
    # In DEV mode the "dev" formatter is forced regardless of MIRACL_LOG_FORMAT.
    # Otherwise, look up the requested format in FORMATTER_MAP.

    if dev_mode:
        active_console_formatter: str = "dev"
    else:
        log_format: str = os.getenv("MIRACL_LOG_FORMAT", "minimal").lower()
        active_console_formatter = FORMATTER_MAP.get(log_format, "console_minimal")

        if log_format not in FORMATTER_MAP:
            print(
                f"[MIRACL] WARNING: Unrecognised MIRACL_LOG_FORMAT={log_format!r}. Falling back to 'minimal'. Valid options: {list(FORMATTER_MAP.keys())}"
            )

    # ------------------------------------------------------------------
    # Formatters
    # ------------------------------------------------------------------
    # All formatters are defined here even if only one is active.
    # dictConfig only instantiates a formatter when a handler references it,
    # so unused entries have zero runtime cost.
    #
    # "console_minimal" → console default
    #     LEVEL: message
    #     No timestamp or logger name — clean for live terminal monitoring.
    #
    # "standard" → file handler default; also available on console via
    #     MIRACL_LOG_FORMAT=verbose
    #     timestamp | LEVEL | logger | message
    #
    # "dev" → auto-selected in DEV mode for both console and file
    #     timestamp | LEVEL | logger | filename:lineno | message
    #
    # "json" → opt-in via MIRACL_LOG_FORMAT=json
    #     Single-line JSON object for log aggregators.

    formatters: dict = {
        "console_minimal": {
            # Minimal format for live terminal monitoring.
            # %(levelname)s — INFO, DEBUG, SUCCESS, WARNING, ERROR, CRITICAL, DEV
            # %(message)s   — the fully formatted message string
            # No timestamp: in a live terminal the time is implicit.
            # No logger name: the message content is usually enough to identify
            # the source at a glance. Full context is always in the log file.
            "format": "%(levelname)s: %(message)s",
        },
        "standard": {
            # Verbose format used by the file handler in all non-DEV runs.
            # Also available on the console via MIRACL_LOG_FORMAT=verbose.
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "dev": {
            # Extends "standard" with source location (file + line number).
            # %(filename)s — the .py filename of the emitting module
            # %(lineno)d   — the exact line number within that file
            # Lets a developer Ctrl+click straight to the source line.
            "format": (
                "%(asctime)s | %(levelname)-8s | %(name)s "
                "| %(filename)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "json": {
            # `()` is dictConfig's syntax for calling an arbitrary factory.
            "()": _JsonFormatter,
        },
    }

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    # Console and file handlers reference different formatters and different
    # level thresholds. They are completely independent — the same LogRecord
    # is passed to both and each applies its own formatter and level check.
    #
    # +-----------------------------------------------------------------+
    # |  root logger  (gate: LOG_LEVEL)                                 |
    # |       |                                                         |
    # |       +-- console handler  (gate: CONSOLE_LOG_LEVEL)            |
    # |       |   formatter: console_minimal / dev                      |
    # |       |                                                         |
    # |       +-- file handler     (gate: 1 — defers to root)           |
    # |           formatter: standard / dev                             |
    # +-----------------------------------------------------------------+

    handlers: dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": active_console_formatter,
            # Now references CONSOLE_LOG_LEVEL instead of LOG_LEVEL.
            # This is the independent console gate. It defaults to INFO so the
            # terminal stays clean even when MIRACL_LOG_LEVEL=DEBUG is set for
            # file capture. Setting MIRACL_CONSOLE_LOG_LEVEL=DEBUG explicitly
            # brings DEBUG output to the terminal as well.
            "level": CONSOLE_LOG_LEVEL,
            "stream": "ext://sys.stdout",
        }
    }

    if FILE_LOGGING_ENABLED:
        log_path: Path = _build_log_path(dev_mode=dev_mode)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            # File handler always uses a verbose formatter so full context is
            # preserved on disk regardless of the console formatter choice.
            "formatter": "dev" if dev_mode else "standard",
            # Floor is set to 1 (below all named levels including DEV=5) so the
            # file handler never independently filters anything out. The root
            # logger (LOG_LEVEL) is the sole gate for what reaches this handler.
            "level": logging.NOTSET,
            "filename": str(log_path),
            "maxBytes": 10_485_760,  # 10 MB/file
            "backupCount": 3,  # keep ~40 MB of history on disk
        }

        print(f"[MIRACL] Logging to file: {log_path}")

    # ------------------------------------------------------------------
    # Apply configuration via dictConfig
    # ------------------------------------------------------------------

    logging.config.dictConfig(
        {
            "version": 1,
            # CRITICAL: must be False.
            # If True (the dictConfig default), any logger created before this
            # call — including those in third-party libraries — is silently disabled.
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "root": {
                "handlers": list(handlers.keys()),
                # LOG_LEVEL is the absolute gate for the entire application.
                # No record below this threshold is processed by any handler,
                # regardless of CONSOLE_LOG_LEVEL or individual logger settings.
                # When LOG_LEVEL="DEV" this becomes 5, allowing DEV records through.
                "level": LOG_LEVEL,
            },
            "loggers": {
                # -- Third-party library silencing ----------------------------
                # Gate noisy libraries at WARNING so their DEBUG/INFO chatter
                # never reaches our handlers. Genuine warnings and errors still
                # propagate to the root handler via propagate: True.
                "matplotlib": {"level": "WARNING", "propagate": True},
                "PIL": {"level": "WARNING", "propagate": True},
                "torch": {"level": "WARNING", "propagate": True},
                "nibabel": {"level": "WARNING", "propagate": True},
                "itk": {"level": "WARNING", "propagate": True},
                # -- Per-module overrides from environment variables -----------
                **_module_overrides(),
            },
        }
    )

    # Flipped only after dictConfig returns successfully. If an exception
    # was raised above, this stays False so the next call can retry.
    _logging_initialized = True
