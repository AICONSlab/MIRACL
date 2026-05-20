"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)
It's part of the backbone for a new iteration of the system architecture for
AICONs Lab's MIRACL.
"""

from argparse import ArgumentParser
from typing import List, Dict, Union, cast, Optional, Any
from pathlib import Path
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl import miracl_logger
from enum import Enum

logger = miracl_logger.logger


class FlagError(Exception):
    """
    Custom exception for flag-related issues.
    """

    def __init__(self, message):
        super().__init__(message)


class MiraclArgumentProcessor:
    class ModuleType(Enum):
        MODULE = "module"
        FLOW_ACE = "ace"
        FLOW_MAPL3 = "mapl3"

    class PathType(Enum):
        FILE = "filepath"
        DIRECTORY = "dirpath"
        CONTENT = "content"

    def __init__(self):
        """
        Initializes the `MiraclArgumentProcessor` instance.
        """
        self.argument_groups = {}

    @staticmethod
    def get_flag_for_module_or_flow(
        obj: MiraclObj, module_type: ModuleType
    ) -> List[str]:
        """
        Returns a list of CLI flags for a MiraclObj instance based on its module type.
        """
        flags = []

        try:
            if module_type == MiraclArgumentProcessor.ModuleType.MODULE:
                if obj.cli_s_flag:
                    flags.append(f"-{obj.cli_s_flag}")
                if obj.cli_l_flag:
                    flags.append(f"--{obj.cli_l_flag}")

            elif hasattr(obj, "flow") and obj.flow:
                flow_flags = obj.flow.get(module_type.value, {})
                if not flow_flags:
                    raise FlagError(
                        f"Flow configuration for {module_type.value} not found in {obj}"
                    )

                if "cli_s_flag" in flow_flags:
                    flags.append(f"-{flow_flags['cli_s_flag']}")
                if "cli_l_flag" in flow_flags:
                    flags.append(f"--{flow_flags['cli_l_flag']}")

            else:
                raise FlagError(
                    f"Invalid object configuration: {obj}. Missing flow attribute."
                )

        except FlagError as e:
            raise e
        except Exception as e:
            raise FlagError(f"Error occurred while processing flags for {obj}: {e}")

        return flags

    def create_parser_arguments(
        self,
        parser: ArgumentParser,
        groups_dict: Dict[str, Dict[str, Union[str, List[MiraclObj]]]],
        module_type: ModuleType = ModuleType.MODULE,
    ) -> None:
        """
        Create argument parser groups based on a dictionary of MiraclObj instances.
        """
        optional_attrs = {
            "cli_obj_type": "type",
            "cli_metavar": "metavar",
            "cli_nargs": "nargs",
            "cli_choices": "choices",
            "obj_default": "default",
            "cli_required": "required",
            "cli_action": "action",
        }

        for group_name, group_info in groups_dict.items():
            title = cast(str, group_info["title"])
            description = cast(Optional[str], group_info.get("description"))

            if "title" not in group_info:
                raise ValueError(
                    f"Invalid group configuration: 'title' missing in {group_name}"
                )

            if group_info["title"] is None:
                raise ValueError(
                    f"Invalid group configuration: 'title' cannot be None in {group_name}"
                )

            if "args" not in group_info:
                raise ValueError(
                    f"Invalid group configuration: 'args' missing in {group_name}"
                )

            if "description" not in group_info:
                raise ValueError(
                    f"Invalid group configuration: 'description' missing in {group_name}"
                )

            if group_info["description"] is None:
                raise ValueError(
                    f"Invalid group configuration: 'description' cannot be None in {group_name}"
                )

            current_group = parser.add_argument_group(
                title=title, description=description
            )
            self.argument_groups[group_name] = current_group

            for obj in group_info["args"]:
                if not isinstance(obj, MiraclObj):
                    raise TypeError(
                        f"Expected MiraclObj, but got {type(obj)}. A valid MiraclObj must be provided."
                    )
                if not hasattr(obj, "cli_help"):
                    raise AttributeError(
                        f"MiraclObj missing 'cli_help' attribute: {obj}"
                    )
                arg_dict = {"help": obj.cli_help}
                for attr, key in optional_attrs.items():
                    if hasattr(obj, attr) and getattr(obj, attr) is not None:
                        value = getattr(obj, attr)
                        if attr == "cli_obj_type":
                            arg_dict[key] = value.python_type
                        else:
                            arg_dict[key] = value

                flags = MiraclArgumentProcessor.get_flag_for_module_or_flow(
                    obj,
                    module_type,
                )

                if flags:
                    current_group.add_argument(*flags, **arg_dict)

    @staticmethod
    def check_path_type(path_str: str) -> PathType:
        """
        Check if the given path string represents a directory, file, or neither.
        """
        try:
            path = Path(path_str)
            if path.is_dir():
                return MiraclArgumentProcessor.PathType.DIRECTORY
            elif path.is_file():
                return MiraclArgumentProcessor.PathType.FILE
            else:
                return MiraclArgumentProcessor.PathType.CONTENT
        except (TypeError, ValueError) as e:
            # logger.error(f"Error checking path type for {path_str}: {e}")
            return MiraclArgumentProcessor.PathType.CONTENT

    def process_miracl_objects(
        self, object_dict: Dict[str, Any], args: Dict[str, Any], module_type: ModuleType
    ) -> None:
        """
        Process MIRACL objects and assign CLI arguments to the appropriate fields.
        """
        args_keys = set(args.keys())

        for obj_name, class_obj in object_dict.items():
            for attr_name, attr_value in class_obj.__dict__.items():
                if isinstance(attr_value, MiraclObj):
                    content_matched = False

                    if module_type == MiraclArgumentProcessor.ModuleType.MODULE:
                        cli_flag = attr_value.cli_l_flag
                        if cli_flag in args_keys:
                            arg_value = args[cli_flag]
                            path_type = self.check_path_type(arg_value)

                            if hasattr(attr_value, path_type.value):
                                setattr(attr_value, path_type.value, arg_value)
                            else:
                                attr_value.content = arg_value

                            content_matched = True
                            print(f"Attribute name: {attr_name}")
                            print(f"Attribute value: {attr_value}")
                            print(f"Assigned to: {path_type}")
                            print(
                                f"Value: {getattr(attr_value, path_type.value, attr_value.content)}\n"
                            )
                    else:
                        if hasattr(attr_value, "flow") and attr_value.flow is not None:
                            flow = attr_value.flow
                            for _, value in flow.items():
                                if isinstance(value, dict) and "cli_l_flag" in value:
                                    flow_cli_flag = value["cli_l_flag"]
                                    if flow_cli_flag in args_keys:
                                        arg_value = args[flow_cli_flag]
                                        path_type = self.check_path_type(arg_value)

                                        if hasattr(attr_value, path_type.value):
                                            setattr(
                                                attr_value, path_type.value, arg_value
                                            )
                                        else:
                                            attr_value.content = arg_value

                                        content_matched = True
                                        print(
                                            f"Flow Attribute name: {attr_name} (from flow)"
                                        )
                                        print(f"Flow Attribute value: {attr_value}")
                                        print(f"Assigned to: {path_type}")
                                        print(
                                            f"Value: {getattr(attr_value, path_type.value, attr_value.content)}\n"
                                        )
                                        break

                    if not content_matched:
                        raise ValueError(
                            f"No matching CLI flag found for attribute '{attr_name}' in object '{obj_name}'."
                        )
