import argparse
from typing import Optional, List, Tuple
from miracl.system.datamodels.miraclobj_serializer import (
    should_include_in_cli,
    miraclobj_to_argparse,
    deserialize_parsed_args_to_objects,
)
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj


class MiraclCLIBuilder:
    def __init__(self, registry, module_type: str):
        self.registry = registry
        self.module_type = module_type
        self.parser = argparse.ArgumentParser(description="My CLI")
        self.groups_cache = {}

    def build_parser(self, parser: Optional[argparse.ArgumentParser] = None):
        # Allow external parser or use the internal one
        if parser:
            self.parser = parser

        registered_entries = self.registry.get_info()
        registered_classes = [
            entry["obj_class"] for entry in registered_entries.values()
        ]

        for cls in registered_classes:
            for name, obj in cls.__dict__.items():
                if isinstance(obj, MiraclObj) and should_include_in_cli(
                    obj, self.module_type
                ):
                    flags, kwargs = miraclobj_to_argparse(obj, self.module_type)

                    cli_group_info = None
                    if obj.flow.get(self.module_type, {}).get("cli_group") is not None:
                        cli_group_info = obj.flow[self.module_type]["cli_group"].value

                    if (
                        cli_group_info
                        and isinstance(cli_group_info, (list, tuple))
                        and len(cli_group_info) >= 2
                    ):
                        group_name, group_desc = cli_group_info[0], cli_group_info[1]
                        if group_name not in self.groups_cache:
                            self.groups_cache[group_name] = (
                                self.parser.add_argument_group(group_name, group_desc)
                            )
                        self.groups_cache[group_name].add_argument(*flags, **kwargs)
                    else:
                        self.parser.add_argument(*flags, **kwargs)
        return self.parser

    def parse(
        self, argv=None, skip_deserialize: bool = False
    ) -> Tuple[argparse.Namespace, Optional[List[MiraclObj]]]:
        # Parse args using the built parser
        args = self.parser.parse_args(argv)

        if skip_deserialize:
            return args, None

        # Gather all MiraclObj instances from registered classes for deserialization
        registered_entries = self.registry.get_info()
        registered_classes = [
            entry["obj_class"] for entry in registered_entries.values()
        ]

        included_objs_list = []
        for cls in registered_classes:
            included_objs_list.extend(
                [
                    obj
                    for obj in cls.__dict__.values()
                    if isinstance(obj, MiraclObj)
                    and should_include_in_cli(obj, self.module_type)
                ]
            )

        parsed_miracl_objs = deserialize_parsed_args_to_objects(
            args, included_objs_list
        )
        return args, parsed_miracl_objs
