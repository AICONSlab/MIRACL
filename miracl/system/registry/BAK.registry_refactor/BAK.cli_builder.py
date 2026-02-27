import argparse
from typing import List, Tuple, Dict, Any, Optional
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.logger import get_logger

logger = get_logger(__name__)


class MiraclCLIBuilder:
    """
    Build an argparse.ArgumentParser from serialized CLI entries.

    Input format expected:
        List[Tuple[flags, kwargs, optional CliGroup]]
    """

    def __init__(self, description: Optional[str] = None):
        logger.info(
            "Initializing CLI builder | description=%s",
            description or "MIRACL CLI",
        )

        self.parser = argparse.ArgumentParser(
            description=description or "MIRACL CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.groups_cache: Dict[str, argparse._ArgumentGroup] = {}

        logger.debug("CLI builder initialized | groups_cache_empty=True")

    def build_parser(
        self, serialized_cli: List[Tuple[List[str], Dict[str, Any], Optional[CliGroup]]]
    ) -> argparse.ArgumentParser:
        logger.info(
            "Building argparse parser | total_entries=%d",
            len(serialized_cli),
        )

        group_creation_count = 0
        argument_count = 0

        for flags, kwargs, cli_group in serialized_cli:
            logger.debug(
                "Attaching CLI argument | flags=%s | group=%s",
                flags,
                cli_group.label if isinstance(cli_group, CliGroup) else None,
            )

            if isinstance(cli_group, CliGroup):
                group_name = cli_group.label
                group_desc = cli_group.description
                if group_name not in self.groups_cache:
                    self.groups_cache[group_name] = self.parser.add_argument_group(
                        group_name, group_desc
                    )

                    group_creation_count += 1
                    logger.debug(
                        "Created CLI argument group | group_name=%s",
                        group_name,
                    )

                self.groups_cache[group_name].add_argument(*flags, **kwargs)
            else:
                self.parser.add_argument(*flags, **kwargs)

            argument_count += 1

        logger.success(
            "Argparse parser built successfully | groups_created=%d | arguments_attached=%d",
            group_creation_count,
            argument_count,
        )

        return self.parser

    # def parse(self, argv: Optional[List[str]] = None) -> argparse.Namespace:
    #     return self.parser.parse_args(argv)
    def parse(self, argv: Optional[List[str]] = None) -> argparse.Namespace:
        logger.info("Parsing CLI arguments")
        logger.debug("Raw argv input | argv=%s", argv)

        namespace = self.parser.parse_args(argv)

        logger.success("CLI parsing complete")
        logger.debug("Parsed namespace | values=%s", vars(namespace))

        return namespace
