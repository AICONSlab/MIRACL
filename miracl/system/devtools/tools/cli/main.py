import sys
from devtools.cli.create_module import create_module


def main() -> None:
    """Entry point for miracl-dev CLI."""
    if len(sys.argv) < 2:
        print("Usage: miracl-dev <command>")
        print("Commands:\n  create-module  Generate a new MIRACL module scaffold")
        return

    command = sys.argv[1]

    if command == "create-module":
        create_module()
    else:
        print(f"Unknown command: {command}")
