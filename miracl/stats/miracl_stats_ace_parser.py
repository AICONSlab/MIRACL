import argparse
import os
from pathlib import Path


class ACEStatsParser:
    def __init__(self) -> None:
        self.parser = self.parsefn()

    def parsefn(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Statistics functions for AI-based Cartography of Ensembles (ACE) segmentation method. These functions assume that the ACE workflow has already been completed."
        )
        # Test flag
        parser.add_argument(
            "-t",
            "--test",
            type=str,
            required=True,
            help="test parser flag",
        )
        return parser


if __name__ == "__main__":
    args_parser = ACEStatsParser()
    args = args_parser.parse_args()
