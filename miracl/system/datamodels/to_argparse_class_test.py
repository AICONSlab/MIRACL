import argparse
from typing import Optional, List, Tuple
from miracl.system.datamodels.miraclobj_serializer import (
    should_include_in_cli,
    miraclobj_to_argparse,
    deserialize_parsed_args_to_objects,
)
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class MiraclCLIBuilder:
    """
    Builder class to create an argparse.ArgumentParser based on registered
    MiraclObj data models and their associated module types.

    This class uses serializer utilities to extract CLI flags, help texts,
    and argument properties from MiraclObj instances, organizes them into
    groups if specified, and provides a unified interface for parsing CLI input.

    Attributes:
        registry: Registry instance containing MiraclObj classes and metadata.
        parser: argparse.ArgumentParser instance being constructed.
        groups_cache: Cache for argparse argument groups to avoid duplicates.
    """

    def __init__(self, registry):
        """
        Initialize the CLI builder with a registry containing MiraclObj
        class definitions and module type metadata.

        Args:
            registry: Object providing access to registered MiraclObj info.
        """
        self.registry = registry
        self.parser = argparse.ArgumentParser(description="My CLI")
        self.groups_cache = {}

    def build_parser(self, parser: Optional[argparse.ArgumentParser] = None):
        """
        Build the argparse parser using MiraclObj definitions from the registry.

        It iterates over registered entries, filters MiraclObj instances
        based on module_type and inclusion criteria, converts them into
        argparse-compatible arguments, and adds them to the parser, optionally
        grouping by CliGroup if specified.

        Args:
            parser (Optional[argparse.ArgumentParser]): An external parser
                to build upon. If None, uses the internal parser.

        Returns:
            argparse.ArgumentParser: The fully constructed parser instance.
        """
        # Allow external parser or use the internal one
        if parser:
            self.parser = parser

        registered_entries = self.registry.get_info()

        for entry in registered_entries.values():
            obj_class = entry["obj_class"]
            module_type = entry["module_type"]  # No fallback, guaranteed present

            for name, obj in obj_class.__dict__.items():
                if isinstance(obj, MiraclObj) and should_include_in_cli(
                    obj, module_type
                ):
                    flags, kwargs = miraclobj_to_argparse(obj, module_type)

                    # ✅ NEW: Handle CliGroup enum properly
                    cli_group_enum = (
                        obj.flow.get(module_type, {}).get("cli_group")
                        if obj.flow
                        else None
                    )

                    if isinstance(cli_group_enum, CliGroup):
                        group_name = cli_group_enum.label
                        group_desc = cli_group_enum.description

                        if group_name not in self.groups_cache:
                            self.groups_cache[group_name] = (
                                self.parser.add_argument_group(group_name, group_desc)
                            )

                        self.groups_cache[group_name].add_argument(*flags, **kwargs)

                    elif cli_group_enum:
                        raise TypeError(
                            f"Invalid cli_group value: {cli_group_enum}. Expected an instance of CliGroup enum, e.g., CliGroup.REQUIRED."
                        )

                    else:
                        # Fallback: add to default (optional) group
                        self.parser.add_argument(*flags, **kwargs)

        return self.parser

    def parse(
        self, argv=None, skip_deserialize: bool = False
    ) -> Tuple[argparse.Namespace, Optional[List[MiraclObj]]]:
        """
        Parse CLI arguments from argv and optionally deserialize parsed values
        back into MiraclObj instances.

        Args:
            argv (Optional[List[str]]): List of CLI arguments to parse.
                Defaults to None, which reads from sys.argv.
            skip_deserialize (bool): If True, skip deserializing parsed args
                into MiraclObj instances. Defaults to False.

        Returns:
            Tuple[argparse.Namespace, Optional[List[MiraclObj]]]:
                - Parsed argparse Namespace.
                - List of updated MiraclObj instances with content set, or None if
                  skip_deserialize is True.
        """
        # Parse args using the built parser
        args = self.parser.parse_args(argv)

        if skip_deserialize:
            return args, None

        registered_entries = self.registry.get_info()
        included_objs_list = []

        for entry in registered_entries.values():
            obj_class = entry["obj_class"]
            module_type = entry["module_type"]  # No fallback, guaranteed present

            included_objs_list.extend(
                [
                    obj
                    for obj in obj_class.__dict__.values()
                    if isinstance(obj, MiraclObj)
                    and should_include_in_cli(obj, module_type)
                ]
            )

        parsed_miracl_objs = deserialize_parsed_args_to_objects(
            args, included_objs_list
        )
        return args, parsed_miracl_objs
