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
    """Custom exception for flag-related issues."""

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

        This constructor sets up the `argument_groups` dictionary, which will store
        the different argument groups created by the `create_parser_arguments` method.

        :return: None
        :rtype: None
        """
        self.argument_groups = {}

    @staticmethod
    def get_flag_for_module_or_flow(
        obj: MiraclObj, module_type: ModuleType
    ) -> List[str]:
        """
        Returns a list of CLI flags for a MiraclObj instance based on its module type.

        This method retrieves flags (both short and long forms) for either a direct module or a flow configuration,
        depending on the value of `module_type`.

        - For a `MODULE`, it uses `cli_s_flag` and `cli_l_flag` attributes.
        - For other module types (e.g., ACE or MAPL3), it checks if the `flow` attribute exists and retrieves flags from there.

        :param obj: The MiraclObj instance whose flags are to be retrieved.
        :type obj: MiraclObj
        :param module_type: The type of the module (either a direct module or part of a workflow).
        :type module_type: ModuleType
        :return: A list of strings representing the flags for the given module or flow.
        :rtype: List[str]
        :raises FlagError: If the configuration for the module or flow is invalid.
        """
        flags = []

        try:
            # Direct flags for ModuleType.MODULE
            if module_type == MiraclArgumentProcessor.ModuleType.MODULE:
                # Append short and long flags if they exist
                if obj.cli_s_flag:
                    flags.append(f"-{obj.cli_s_flag}")
                if obj.cli_l_flag:
                    flags.append(f"--{obj.cli_l_flag}")

            # Flow flags for other module types (ACE, MAPL3, etc.)
            elif hasattr(obj, "flow") and obj.flow:
                flow_flags = obj.flow.get(module_type.value, {})
                if not flow_flags:
                    raise FlagError(
                        f"Flow configuration for {module_type.value} not found in {obj}"
                    )

                # Use flow-specific flags
                if "cli_s_flag" in flow_flags:
                    flags.append(f"-{flow_flags['cli_s_flag']}")
                if "cli_l_flag" in flow_flags:
                    flags.append(f"--{flow_flags['cli_l_flag']}")

            else:
                raise FlagError(
                    f"Invalid object configuration: {obj}. Missing flow attribute."
                )

        except FlagError as e:
            raise e  # Re-raise the custom error
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

        This method adds argument groups to an ArgumentParser instance for each group
        defined in the provided `groups_dict`. Each group is expected to contain a
        'title', 'description', and 'args', which are used to define the group title,
        description, and the individual arguments for the group, respectively.

        The method will:
        - Validate that each group contains the required fields ('title', 'args', and 'description').
        - Create an argument group in the parser using the provided 'title' and 'description'.
        - Add the arguments defined in each group to the parser.

        :param parser: The ArgumentParser instance to which argument groups will be added.
        :type parser: ArgumentParser
        :param groups_dict: A dictionary where the keys are group names, and the values are dictionaries
                            containing 'title', 'description', and 'args' (a list of MiraclObj instances).
        :type groups_dict: Dict[str, GroupInfoType]
        :param module_type: A module type (e.g., MODULE, ACE, MAPL3) to determine which flags to use. Defaults to MODULE.
        :type module_type: ModuleType, optional
        :return: None
        :rtype: None
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
            logger.debug(
                f"group_name: {group_name}"
            )  # Groups passed from argparser dict
            logger.debug(
                f"group_info: {group_info}"
            )  # Title, description etc. of group and corresponding MIRACL objects
            # Extract title and description from dict
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

            # Assign title and description to a new argument group
            current_group = parser.add_argument_group(
                title=title, description=description
            )
            self.argument_groups[group_name] = (
                current_group  # Add argument group to groups dict with name of group
            )

            # Iterates over the list of MiraclObj instances in each group
            for obj in group_info["args"]:
                if not isinstance(
                    obj, MiraclObj
                ):  # Check if obj is not an instance of MiraclObj
                    raise TypeError(
                        f"Expected MiraclObj, but got {type(obj)}. A valid MiraclObj must be provided."
                    )
                # Starts by creating a dictionary that will hold MIRACL objs argument options, beginning with 'help'
                if not hasattr(obj, "cli_help"):
                    raise AttributeError(
                        f"MiraclObj missing 'cli_help' attribute: {obj}"
                    )
                arg_dict = {"help": obj.cli_help}
                # Iterates through the predefined optional attributes (cli_obj_type, cli_metavar, etc.) and assigns them if av ailable in obj
                for attr, key in optional_attrs.items():
                    # Checks if the MiraclObj has the given attribute and if its value is not None
                    if hasattr(obj, attr) and getattr(obj, attr) is not None:
                        value = getattr(obj, attr)
                        # For cli_obj_type, the value is expected to be a type, so it is added as `python_type` in the argument dictionary.
                        if attr == "cli_obj_type":
                            arg_dict[key] = value.python_type
                        else:
                            arg_dict[key] = value

                flags = MiraclArgumentProcessor.get_flag_for_module_or_flow(
                    obj,
                    module_type,
                )

                if flags:
                    logger.debug(f"ARG DICT: {arg_dict}")
                    current_group.add_argument(*flags, **arg_dict)

    @staticmethod
    def check_path_type(path_str: str) -> PathType:
        """
        Check if the given path string represents a directory, file, or neither.

        This method determines whether the provided string is a valid directory,
        file, or content path by checking the existence of the path.

        :param path_str: The path string to check
        :type path_str: str
        :return: A `PathType` enum indicating the type ('FILE', 'DIRECTORY', 'CONTENT')
        :rtype: PathType
        :raises ValueError: If there is an issue checking the path type.
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
            logger.error(f"Error checking path type for {path_str}: {e}")
            return MiraclArgumentProcessor.PathType.CONTENT

    def process_miracl_objects(
        self, object_dict: Dict[str, Any], args: Dict[str, Any], module_type: ModuleType
    ) -> None:
        """
        Process MIRACL objects and assign CLI arguments to the appropriate fields.

        This method iterates over the provided `object_dict` (which maps object names
        to MIRACL objects), retrieves the relevant command-line arguments from `args`,
        and assigns them to the correct fields in each MIRACL object based on the module type.

        It supports direct flags (`cli_s_flag` and `cli_l_flag`) and flow-specific flags
        (when the `module_type` is part of a flow). It also checks the type of the path
        and assigns the value accordingly.

        :param object_dict: A dictionary of MIRACL objects, where keys are object names and values are the corresponding objects.
        :type object_dict: Dict[str, Any]
        :param args: A dictionary of parsed CLI arguments.
        :type args: Dict[str, Any]
        :param module_type: The module type (either `MODULE`, `FLOW_ACE`, etc.), which determines which flags to use.
        :type module_type: ModuleType
        :raises ValueError: If no matching CLI flag is found for an attribute.
        :return: None
        :rtype: None
        """
        args_keys = set(args.keys())

        for obj_name, class_obj in object_dict.items():
            for attr_name, attr_value in class_obj.__dict__.items():
                if isinstance(attr_value, MiraclObj):
                    # Initialize content as None to track if a match was found
                    content_matched = False

                    # Look for direct flags first (cli_s_flag or cli_l_flag) for MODULE type
                    if module_type == MiraclArgumentProcessor.ModuleType.MODULE:
                        cli_flag = attr_value.cli_l_flag
                        if cli_flag in args_keys:
                            arg_value = args[cli_flag]
                            path_type = self.check_path_type(arg_value)

                            # Set the attribute based on the detected path type
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
                        # If module_type is not ModuleType.MODULE, check for flow flags
                        if hasattr(attr_value, "flow") and attr_value.flow is not None:
                            flow = attr_value.flow
                            # Look for flow-specific flags (cli_l_flag inside the flow)
                            for _, value in flow.items():
                                if isinstance(value, dict) and "cli_l_flag" in value:
                                    flow_cli_flag = value["cli_l_flag"]
                                    if flow_cli_flag in args_keys:
                                        # Flow flag match found, process the argument
                                        arg_value = args[flow_cli_flag]
                                        path_type = self.check_path_type(arg_value)

                                        # Set the attribute based on the detected path type
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
                                        break  # Exit the loop once a match is found

                    # Raise an error if no match was found for either direct flags or flow flags
                    if not content_matched:
                        raise ValueError(
                            f"No matching CLI flag found for attribute '{attr_name}' in object '{obj_name}'."
                        )


# Usage:
# processor = MiraclArgumentProcessor(parser)
# processor.create_parser_arguments(groups_dict)
# result = processor.process_miracl_objects(class_list, args)


# Usage example:
# parser = ArgumentParser()
# processor = MiraclArgumentProcessor(parser)
# processor.create_parser_arguments(groups_dict)
# args = parser.parse_args()
# result = processor.process_miracl_objects(class_list, vars(args))
