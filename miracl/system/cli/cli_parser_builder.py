import argparse
from typing import List, Tuple, Dict, Any, Optional
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.logger import get_logger
from miracl.system.cli.cli_parser_contracts import SerializedCLI

logger = get_logger(__name__)


class MiraclCLIBuilder:
    """
    Build an argparse.ArgumentParser from serialized CLI entries.

    Input format expected:
        List[Tuple[flags, kwargs, optional CliGroup]]
    """

    def __init__(self):
        logger.info("Initializing CLI builder")

        self.parser: argparse.ArgumentParser
        self.groups_cache: Dict[str, argparse._ArgumentGroup] = {}

        logger.debug("CLI builder initialized | groups_cache_empty=True")

    def build_parser(
        self,
        serialized: SerializedCLI,
    ) -> argparse.ArgumentParser:
        logger.info(
            "Building argparse parser | total_entries=%d",
            len(serialized.args),
        )

        self.parser = argparse.ArgumentParser(
            description=self._build_description(serialized.meta),
            epilog=self._build_epilog(serialized.meta),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.groups_cache = {}

        group_creation_count = 0
        argument_count = 0

        for flags, kwargs, cli_group in serialized.args:
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

    @staticmethod
    def _build_description(meta: Any) -> str:
        """
        Build argparse description string from _meta block params provided in YAML config.
        """
        parts = []

        if meta.experimental:
            parts.append("[EXPERIMENTAL]")

        if meta.deprecated:
            parts.append(f"[DEPRECATED: {meta.deprecation_message}]")

        parts.append(meta.help)

        return " ".join(parts)

    @staticmethod
    def _build_epilog(meta: Any) -> Optional[str]:
        """
        Build argparse epilog string from _meta block content.
        """
        parts = []

        if meta.extended_help:
            parts.append(meta.extended_help)

        if meta.examples:
            parts.append("Examples:")
            for ex in meta.examples:
                parts.append(f"  {ex.cmd}")
                if ex.help:
                    parts.append(f"  +--> {ex.help}")

        runtime_parts = []
        if meta.estimated_runtime:
            runtime_parts.append(f"Runtime : {meta.estimated_runtime}")
        if meta.min_memory_gb:
            runtime_parts.append(f"Memory  : {meta.min_memory_gb}")
        if meta.requires_gpu:
            runtime_parts.append("GPU     : required")
        if meta.version:
            runtime_parts.append(f"Version : {meta.version}")
        if runtime_parts:
            parts.append("\n" + "\n".join(runtime_parts))

        if meta.docs_url:
            parts.append(f"\nFor more details, see: {meta.docs_url}")

        return "\n".join(parts) if parts else None

    def parse(self, argv: Optional[List[str]] = None) -> argparse.Namespace:
        logger.info("Parsing CLI arguments")
        logger.debug("Raw argv input | argv=%s", argv)

        namespace = self.parser.parse_args(argv)

        logger.success("CLI parsing complete")
        logger.debug("Parsed namespace | values=%s", vars(namespace))

        return namespace
