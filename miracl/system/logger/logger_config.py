"""
Code written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Central logging configuration for the MIRACL pipeline.

This module is the single source of truth for how logging is set up across the entire
application. It should never be imported directly by pipeline modules. Those should use
get_logger() from __init__.py instead.

- Configuration is done once via dictConfig, which is declarative and easier to reason
  about than imperative handler/formatter construction.
- _logging_initialized ensures that importing this module from many places never causes
  duplicate log output.
- Log level, file logging, and per-module overrides are driven by environment variables
  so that operators can change verbosity without modifying source code. This is
  especially useful in containerised (Docker/Singularity) runs which are the main
  usecase of MIRACL currently.
- Third-party libraries are silenced at the named-logger level rather than by filtering
  on the root, so MIRACL's own DEBUG output is unaffected.
- File logging is enabled by default and writes to a central log directory. Each run
  produces a uniquely named file (<script>_<timestamp>.log) so logs from different runs
  never overwrite each other.
- The console and file handlers use independent level thresholds. This means setting
  MIRACL_LOG_LEVEL=DEBUG captures a full DEBUG trace in the log file while keeping the
  terminal clean at INFO. See the environment variable documentation below for the
  interaction rules.
- The console uses a minimal formatter by default (LEVEL: message) while the log file
  always uses the full verbose format with timestamps.
- When MIRACL_LOG_LEVEL=DEV, a dedicated "dev" formatter is used that includes source
filename and line number, and logs are written to a separate dev/ subdirectory.

MIRACL_LOG_LEVEL: Global log level. Acts as the absolute floor for the entire application. No record
    below this threshold is processed by any handler. Accepted values are DEV, DEBUG,
    INFO, WARNING, ERROR, CRITICAL (case-insensitive). Default: INFO

MIRACL_LOG_LEVEL sets the root logger gate. MIRACL_CONSOLE_LOG_LEVEL can only raise
    the console threshold above it. It cannot lower it below.

MIRACL_CONSOLE_LOG_LEVEL: Level threshold for the console handler specifically.
    Defaults to INFO so the terminal stays clean even when MIRACL_LOG_LEVEL is set to
    DEBUG or DEV for file capture purposes. Accepted values: same as MIRACL_LOG_LEVEL.
    Default: INFO

MIRACL_LOG_LEVEL_<MODULE>: Per-module override. The suffix is translated into a dotted
    Python module path by lower-casing and replacing underscores with dots, then
    prepending "miracl.".

MIRACL_LOG_FORMAT: Console output format. Valid values: "minimal" (default),
    "verbose", "json", "dev".
    "minimal"  -> LEVEL: message                       (default, clean terminal output)
    "verbose"  -> timestamp | LEVEL | logger | message (same as the log file)
    "json"     -> single-line JSON object              (containers / log aggregators)
    "dev"      -> set automatically when MIRACL_LOG_LEVEL=DEV; adds file + line number

MIRACL_LOG_TO_FILE: Set to false to disable file logging entirely. Useful in unit tests
    or environments where the runtime captures stdout. Default: true (file logging is
    on).

MIRACL_LOG_DIR: Directory where log files are written.
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


#######################################################################################
# Custom log level: DEV
#######################################################################################
# DEV sits at level 5, below all standard levels:
#
#   DEV      =  5 <- step-by-step execution trace for active codebase exploration
#   DEBUG    = 10 <- internal state, parameters, computed values
#   INFO     = 20 <- user-facing progress
#   SUCCESS  = 25 <- pipeline stage completed cleanly
#   WARNING  = 30 <- unexpected but recoverable
#   ERROR    = 40 <- operation failed
#   CRITICAL = 50 <- unrecoverable
#
# DEV is intended for a developer who is unfamiliar with the codebase and wants to
# understand execution flow at a granular level. Intermediate variable states, control
# flow decisions, loop iterations, data shapes at every transformation step, and so on.

DEV: int = 5
logging.addLevelName(DEV, "DEV")


def _dev(self: logging.Logger, message: str, *args, **kwargs) -> None:
    """
    Emit a log record at the custom DEV level (5).
    """
    if self.isEnabledFor(DEV):
        self._log(DEV, message, args, **kwargs)


logging.Logger.dev = _dev


#######################################################################################
# CUSTOM LOG LEVEL: SUCCESS
#######################################################################################

SUCCESS: int = 25
logging.addLevelName(SUCCESS, "SUCCESS")


def _success(self: logging.Logger, message: str, *args, **kwargs) -> None:
    """
    Emit a log record at the custom SUCCESS level (25).
    """
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


logging.Logger.success = _success


#######################################################################################
# PROCESS-WIDE INITIALISATION GUARD
#######################################################################################

_logging_initialized: bool = False


#######################################################################################
# LOG LEVEL CONSTANTS
#######################################################################################

LOG_LEVEL: str = os.getenv(
    "MIRACL_LOG_LEVEL",
    "DEBUG",
).upper()
CONSOLE_LOG_LEVEL: str = os.getenv(
    "MIRACL_CONSOLE_LOG_LEVEL",
    "DEBUG",
).upper()


FORMATTER_MAP: Dict[str, str] = {
    "minimal": "console_minimal",  # default: "LEVEL: message"
    "verbose": "standard",  # opt-in: full timestamp format
    "json": "json",  # structured output for aggregators
    "dev": "dev",  # auto-set in DEV mode -> adds file and lineno
    # "colored": "colored",
}


#######################################################################################
# File logging configuration
#######################################################################################

FILE_LOGGING_ENABLED: bool = os.getenv("MIRACL_LOG_TO_FILE", "true").lower() != "false"

LOG_DIR: Path = Path(os.getenv("MIRACL_LOG_DIR", "/code/miracl/logs")).expanduser()


def _build_log_path(dev_mode: bool = False) -> Path:
    """
    Derive a timestamped log file path from the invoking script's name.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        main_module = sys.modules.get("__main__")
        script_stem = Path(main_module.__file__).stem
    except (AttributeError, TypeError):
        script_stem = "miracl"

    parent = LOG_DIR / "dev" if dev_mode else LOG_DIR
    return parent / f"{script_stem}_{timestamp}.log"


#######################################################################################
# PER-MODULE OVERRIDE BUILDER
#######################################################################################


def _module_overrides() -> dict:
    """
    Scan environment variables and build per-module logger config entries.
    """
    overrides: dict = {}
    prefix: str = "MIRACL_LOG_LEVEL_"

    for key, val in os.environ.items():
        if not key.startswith(prefix):
            continue

        module_path = "miracl." + key[len(prefix) :].lower().replace("_", ".")

        overrides[module_path] = {
            "level": val.upper(),
            "propagate": True,
        }

    return overrides


#######################################################################################
# JSON FORMATTER
#######################################################################################


class _JsonFormatter(logging.Formatter):
    """
    Emit each log record as a single-line JSON object.

    Useful when MIRACL runs inside a container and logs are shipped to an aggregator
    that can parse structured fields. Enable by setting MIRACL_LOG_FORMAT=json in the
    environment.
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


#######################################################################################
# MAIN SETUP FUNCTION
#######################################################################################


def setup_logging() -> None:
    """
    Configure the root logger and all handlers for the MIRACL application.
    """
    global _logging_initialized

    if _logging_initialized:
        return

    dev_mode: bool = LOG_LEVEL == "DEV"

    if dev_mode:
        active_console_formatter: str = "dev"
    else:
        log_format: str = os.getenv("MIRACL_LOG_FORMAT", "minimal").lower()
        active_console_formatter = FORMATTER_MAP.get(log_format, "console_minimal")

        if log_format not in FORMATTER_MAP:
            print(
                f"[MIRACL] WARNING: Unrecognised MIRACL_LOG_FORMAT={log_format!r}. Falling back to 'minimal'. Valid options: {list(FORMATTER_MAP.keys())}"
            )

    formatters: dict = {
        "console_minimal": {
            "format": "%(levelname)s: %(message)s",
        },
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "dev": {
            "format": (
                "%(asctime)s | %(levelname)-8s | %(name)s "
                "| %(filename)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "json": {
            "()": _JsonFormatter,
        },
    }

    handlers: dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": active_console_formatter,
            "level": CONSOLE_LOG_LEVEL,
            "stream": "ext://sys.stdout",
        }
    }

    if FILE_LOGGING_ENABLED:
        log_path: Path = _build_log_path(dev_mode=dev_mode)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "dev" if dev_mode else "standard",
            "level": logging.NOTSET,
            "filename": str(log_path),
            "maxBytes": 10_485_760,  # 10 MB/file
            "backupCount": 3,
        }

        print(f"[MIRACL] Logging to file: {log_path}")
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "root": {
                "handlers": list(handlers.keys()),
                "level": LOG_LEVEL,
            },
            "loggers": {
                "matplotlib": {"level": "WARNING", "propagate": True},
                "PIL": {"level": "WARNING", "propagate": True},
                "torch": {"level": "WARNING", "propagate": True},
                "nibabel": {"level": "WARNING", "propagate": True},
                "itk": {"level": "WARNING", "propagate": True},
                **_module_overrides(),
            },
        }
    )

    _logging_initialized = True
