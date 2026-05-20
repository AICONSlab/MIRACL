"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Simply API for the miracl.system.runtime package.

Defines what is exported with:
  from miracl.system.runtime import MiraclRuntime
  from miracl.system.runtime import RuntimeArgs

Why?
  - Stable import paths: If `iraclRuntime is ever moved to a different sub-module,
    updating this file is the only change required for call sites to keep working.
  - Explicit public surface: Anything not listed here is considered an internal
    implementation detail and should not be imported directly by callers outside this
    package.

Runtime layout:
  miracl/system/runtime/
  |-- __init__.py          <- re-exports
  |-- bootstrap.py         <- configure_runtime called before any imports
  |-- runtime_parser.py    <- parser and parser dataclass
  |-- frontend.py          <- Frontende adapters and dispatcher and all adapters
  |-- runtime.py           <- Orchestration

Usage:
  from miracl.system.runtime.bootstrap import configure_runtime
  configure_runtime()   # Run first before other imports!! Runtime configuration!!

  from miracl.system.runtime import MiraclRuntime

  runtime = MiraclRuntime(
      registry_config="/path/to/modules.yaml",
      workflow_config="/path/to/workflow.yaml",
  )
  runtime.run()

Note:
  configure_runtime is intentionally not reexported here since it must be called before
  this package is imported!!
"""


# HACK: This is lazy loaded to suppress logging when the help flags are called. Maybe
# this could be done more elegantly as lazy loading does add to the loading time of the
# help text. I mean it's milliseconds so it's fine, the user is not going to notice a
# difference, but I would like to optimize this properly at some point.
def __getattr__(name):
    if name == "MiraclRuntime":
        from miracl.system.runtime.runtime import MiraclRuntime

        return MiraclRuntime
    if name == "RuntimeArgs":
        from miracl.system.runtime.runtime_parser import RuntimeArgs

        return RuntimeArgs
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# NOTE: Leaving this here as a ref in case I can find a better solution for the above
# hack.
# from miracl.system.runtime.runtime import MiraclRuntime
# from miracl.system.runtime.runtime_parser import (
#     RuntimeArgs,
# )  # RuntimeArgs is the data contract between RuntimeArgParser and MiraclRuntime.

__all__ = [
    "MiraclRuntime",
    "RuntimeArgs",
]
