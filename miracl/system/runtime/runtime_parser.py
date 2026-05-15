"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

This parser is only here to inspect sys.argv for MIRACL runtime level flags like --gui
or --dry-run. It returns a plain RuntimeArgs dataclass for the results.

I split this from the original runtime script. Mostly because I like modularity and
clarity and it also makes it easier to test this class. This is much better also
because it now has exactly one task and I can easily extend it.
"""

import sys
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


#######################################################################################
# DATA MODEL
#######################################################################################


@dataclass
class RuntimeArgs:
    """
    Plain data container for the runtime level flags extracted from sys.argv. They come
    from RuntimeArgParser.

    Args:
        frontend (frontend): The name of the frontend engine to use for gathering user
        inputs. Defaults to "cli" when --gui is absent. Valid values are defined by
        FrontendDispatcher._registry. Maybe I should adpat enums here as well.
        dry_run (bool): When True, the runtime generates execution plans but does not
        invoke any runners. Useful for inspecting what would be executed without side
        effects.
    """

    frontend: str = "cli"
    dry_run: bool = False


#######################################################################################
# PARSER
#######################################################################################


class RuntimeArgParser:
    """
    Parses MIRACL runtime-level flags from sys.argv and returns a RuntimeArgs dataclass.

    Importantly, this class operates on a copy of sys.argv internally and only writes
    back to sys.argv once namely at the end of the parse method. The idea here is that
    the mutation is a single, explicit, auditable step rather than a series of in-place
    removals scattered across ``__init__`` helper methods like it was before I started
    refactoring this code.

    After parse returns, sys.argv contains only the flags that were not consumed here.
    In other words, the module-level flags that the downstream CLI adapter from the
    MIRACL builder is supposed to parse.

    Flags:
      --gui [engine]: Selects a GUI frontend. The optional engine token can currently
                      be pyqt or gradio (although the latter doesn't work atm). If the
                      token is absent or not a recognised engine name, pyqt is used as
                      the default GUI engine. For our current user base this will
                      likely be the frontend they want. Without the --gui flag, the
                      frontend defaults to cli.
      --dry-run: Boolean flag that, when present, lets the runtime generate execution
                 plans without invoking any runners.
    """

    VALID_GUI_ENGINES: List[str] = [
        "pyqt",
        "gradio",
    ]

    def parse(self, argv: Optional[List[str]] = None) -> RuntimeArgs:
        """
        Extract runtime-level flags and return a populated RuntimeArgs.

        When argv is None, sys.argv[1:] gets rewritten to contain only the flags that
        were not consumed here. This is the contract that downstream adapters like
        cli and PyQt depend on. By the time they receive sys.argv, the runtime flags
        are long gone.

        Args:
            argv (argv): The argument list to parse. When None (the default),
                         sys.argv[1:]`` is used. Passing an explicit list is
                         recommended in tests so that the real sys.argv is never
                         touched.
        Returns:
            RuntimeArgs: RuntimeArgs instance carrying the extracted values.

        """
        # Work on a local copy so that the parsing logic is free to mutate the list
        # without touching the real sys.argv until everything is done.
        using_real_argv = argv is None
        working = list(sys.argv[1:]) if using_real_argv else list(argv)

        frontend = self._extract_frontend(working)
        dry_run = self._pop_flag(working, "--dry-run")

        if using_real_argv:
            sys.argv[1:] = working
            logger.debug(
                "sys.argv updated after runtime flag extraction | remaining=%s",
                sys.argv[1:],
            )

        args = RuntimeArgs(frontend=frontend, dry_run=dry_run)

        logger.debug(
            "RuntimeArgs resolved | frontend=%s | dry_run=%s",
            args.frontend,
            args.dry_run,
        )

        return args

    ###################################################################################
    # PRIVATE HELPERS
    ###################################################################################

    def _extract_frontend(self, argv: List[str]) -> str:
        """
        Looks for --gui [engine] in argv, removes the matched tokens and returns the
        selected frontend name.

        The method mutates argv in place so that the caller's working copy is kept
        clean for the following flag extractions.

        Logic:
            - --gui absent: returns cli. Default if no GUI is requested.
            - --gui present: next token is a valid engine name. Removes both tokens and
              returns that engine name.
            - --gui present: next token is absent or not a valid engine. Removes only
              --gui and returns pyqt, which is currently the default GUI engine.

        Args:
            argv (argv: list[str]): Mutable working copy of the argument list.

        Returns:
            str: The selected frontend name.
        """
        if "--gui" not in argv:
            return "cli"

        idx = argv.index("--gui")

        # Remove the --gui flag itself from the working copy.
        argv.pop(idx)

        # Check whether the token that now sits at `idx` (i.e. the token that
        # immediately followed --gui) is a recognised engine name. If so, consume it
        # too! Otherwise leave it in place as it belongs to the module-level argument
        # parser.
        if idx < len(argv) and argv[idx] in self.VALID_GUI_ENGINES:
            engine = argv.pop(idx)
            logger.debug("GUI engine explicitly requested | engine=%s", engine)
            return engine

        # --gui was present but no valid engine name followed it. Currently falls back
        # to the default GUI engine i.e. pyqt.
        logger.debug("--gui present with no explicit engine; defaulting to 'pyqt'")
        return "pyqt"

    def _pop_flag(self, argv: List[str], flag: str) -> bool:
        """
        Remove a boolean flag from argv if it is present and return whether it was
        found. Mutates argv in place.

        Args:
            argv (list[str]): Mutable working copy of the argument list.
            flag (str): The exact flag string to look for e.g. --dry-run.

        Returns:
            bool: True if the flag was present and has been removed and False otherwise.
        """
        if flag in argv:
            argv.remove(flag)
            logger.debug("Runtime flag found and removed | flag=%s", flag)
            return True
