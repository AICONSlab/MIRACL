# from argparse import ArgumentParser, _ArgumentGroup
# from typing import List, Dict, Union, cast, Optional, Any
#
#
# def create_parser_arguments(
#     parser: ArgumentParser,
#     groups_dict: Dict[str, Dict[str, Union[str, List[Any]]]],
#     module_type: str = "module",
# ) -> Dict[str, _ArgumentGroup]:
#     """
#     Create argument parser groups based on a dictionary of MiraclObj instances.
#
#     Each group will contain command-line arguments defined by the attributes
#     of the MiraclObj instances.
#
#     :param parser: The ArgumentParser instance to which the arguments will be added.
#     :param groups_dict: A dictionary mapping group names to lists of MiraclObj instances and descriptions.
#     :param module_type: A string differentiating between a stand-alone module or a module as part of a workflow.
#     :return: A dictionary of argument groups.
#     """
#     optional_attrs = {
#         "cli_obj_type": "type",
#         "cli_metavar": "metavar",
#         "cli_nargs": "nargs",
#         "cli_choices": "choices",
#         "obj_default": "default",
#         "cli_required": "required",
#         "cli_action": "action",
#     }
#
#     # Dict to return parser args groups for custom ACE flow help
#     argument_groups = {}
#
#     for group_name, group_info in groups_dict.items():
#         title = cast(str, group_info["title"])
#         description = cast(
#             Optional[str],
#             group_info.get("description"),
#         )
#
#         current_group = parser.add_argument_group(
#             title=title,
#             description=description,
#         )
#         argument_groups[group_name] = current_group
#
#         for obj in group_info["args"]:
#             arg_dict = {"help": obj.cli_help}
#             for attr, key in optional_attrs.items():
#                 if hasattr(obj, attr) and getattr(obj, attr) is not None:
#                     value = getattr(obj, attr)
#                     if attr == "cli_obj_type":
#                         arg_dict[key] = value.python_type
#                     else:
#                         arg_dict[key] = value
#
#             if module_type == "module":
#                 flags = [f"-{obj.cli_s_flag}" for obj in [obj] if obj.cli_s_flag]
#                 flags.extend(f"--{obj.cli_l_flag}" for obj in [obj] if obj.cli_l_flag)
#             else:
#                 flags = []
#                 if hasattr(obj, "flow") and obj.flow and module_type in obj.flow:
#                     if (
#                         "cli_s_flag" in obj.flow[module_type]
#                         and obj.flow[module_type]["cli_s_flag"]
#                     ):
#                         flags.append(f"-{obj.flow[module_type]['cli_s_flag']}")
#                     if (
#                         "cli_l_flag" in obj.flow[module_type]
#                         and obj.flow[module_type]["cli_l_flag"]
#                     ):
#                         flags.append(f"--{obj.flow[module_type]['cli_l_flag']}")
#                 else:
#                     if hasattr(obj, "cli_s_flag") and obj.cli_s_flag:
#                         flags.append(f"-{obj.cli_s_flag}")
#                     if hasattr(obj, "cli_l_flag") and obj.cli_l_flag:
#                         flags.append(f"--{obj.cli_l_flag}")
#
#             if flags:
#                 current_group.add_argument(*flags, **arg_dict)
#
#     return argument_groups
#
#
# def check_path_type(path_str: str) -> str:
#     """
#     Check if the given path string represents a directory, file, or neither.
#
#     :param path_str: The path string to check
#     :type path_str: str
#     :return: 'dirpath' if it's a directory, 'filepath' if it's a file, 'content' otherwise
#     :rtype: str
#     """
#     try:
#         path = Path(path_str)
#         if path.is_dir():
#             return "dirpath"
#         elif path.is_file():
#             return "filepath"
#         else:
#             return "content"
#     except (TypeError, ValueError):
#         return "content"
#
#
# def process_miracl_objects(
#     class_list: List[str], args: Dict[str, Any]
# ) -> Dict[str, Dict[str, Any]]:
#     """
#     Process MiraclObj attributes and assign CLI arguments to appropriate fields.
#
#     This function iterates through the attributes of specified classes,
#     matches CLI arguments to the appropriate MiraclObj attributes,
#     and assigns values based on whether they represent file paths,
#     directory paths, or general content.
#
#     :param class_list: List of class names to process
#     :type class_list: list of str
#     :param args: Dictionary of parsed CLI arguments
#     :type args: dict
#
#     :raises ValueError: If no matching CLI flag is found for an attribute
#     """
#     args_keys = set(args.keys())  # Convert to set for faster lookup
#
#     updated_miracl_objects = {class_name: {} for class_name in class_list}
#
#     for class_name in class_list:
#         class_obj = globals()[class_name]
#         for attr_name, attr_value in class_obj.__dict__.items():
#             if isinstance(attr_value, MiraclObj):
#                 # Initialize content as None
#                 # This will be used to check if the content attribute has been
#                 # assigned correctly i.e. if there is a match for the cli arg
#                 content_matched = False
#
#                 cli_flag = attr_value.cli_l_flag
#                 if cli_flag in args_keys:
#                     arg_value = args[cli_flag]
#                     path_type = check_path_type(arg_value)
#
#                     if hasattr(attr_value, path_type):
#                         setattr(attr_value, path_type, arg_value)
#                     else:
#                         attr_value.content = arg_value
#
#                     content_matched = True
#                     print(f"Attribute name: {attr_name}")
#                     print(f"Attribute value: {attr_value}")
#                     print(f"Assigned to: {path_type}")
#                     print(
#                         f"Value: {getattr(attr_value, path_type, attr_value.content)}\n"
#                     )
#                 else:
#                     # If there is no match for the module flag, the assumption is
#                     # that the module is being evoked as part of a workflow hence
#                     # the flow attribute will be checked for a match
#                     if "flow" in attr_value.__dict__ and attr_value.flow is not None:
#                         flow = attr_value.flow
#                         for key, value in flow.items():
#                             if isinstance(value, dict) and "cli_l_flag" in value:
#                                 flow_cli_flag = value["cli_l_flag"]
#                                 if flow_cli_flag in args_keys:
#                                     arg_value = args[flow_cli_flag]
#                                     path_type = check_path_type(arg_value)
#
#                                     if hasattr(attr_value, path_type):
#                                         setattr(attr_value, path_type, arg_value)
#                                     else:
#                                         attr_value.content = arg_value
#
#                                     content_matched = True
#                                     print(
#                                         f"Flow Attribute name: {attr_name} (from flow)"
#                                     )
#                                     print(f"Flow Attribute value: {attr_value}")
#                                     print(f"Assigned to: {path_type}")
#                                     print(
#                                         f"Value: {getattr(attr_value, path_type, attr_value.content)}\n"
#                                     )
#                                     break
#
#                 # This check should technically be redundant as a match should be
#                 # guaranteed because of how the Pydantic objects are set up and
#                 # handled. However, I leave it in here as an additional check as
#                 # it practially has zero overhead.
#                 if not content_matched:
#                     raise ValueError(
#                         f"No matching CLI flag found for attribute '{attr_name}' in class '{class_name}'."
#                     )
#
#                 updated_miracl_objects[class_name][attr_name] = attr_value
#
#     return updated_miracl_objects
#
#
# # class_list = ["seg_inference", "seg_mapl3_genpatch"]
# # args_keys = set(args.keys())  # Convert to set for faster lookup
# # miracl_objs_dict = process_miracl_objects(class_list, args)
# #
# # print(f"\n\nOutput from global context: {seg_mapl3_genpatch.output.dirpath}")
# # print(
# #     f"\n\nOutput from dictionary: {miracl_objs_dict['seg_mapl3_genpatch']['output'].dirpath}"
# # )
# # print(f"\n\nMIRACL objs dict: {miracl_objs_dict}")
# #

from argparse import ArgumentParser, _ArgumentGroup
from typing import List, Dict, Union, cast, Optional, Any
from pathlib import Path
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj


class MiraclArgumentProcessor:
    def __init__(self, parser: ArgumentParser):
        """
        Initialize the MiraclArgumentProcessor with an ArgumentParser.

        :param parser: The ArgumentParser instance to be used for creating arguments
        """
        self.parser = parser
        self.argument_groups = {}

    def create_parser_arguments(
        self,
        groups_dict: Dict[str, Dict[str, Union[str, List[Any]]]],
        module_type: str = "module",
    ) -> None:
        """
        Create argument parser groups based on a dictionary of MiraclObj instances.

        Each group will contain command-line arguments defined by the attributes
        of the MiraclObj instances.

        :param groups_dict: A dictionary mapping group names to lists of MiraclObj instances and descriptions.
        :param module_type: A string differentiating between a stand-alone module or a module as part of a workflow.
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

            current_group = self.parser.add_argument_group(
                title=title, description=description
            )
            self.argument_groups[group_name] = current_group

            for obj in group_info["args"]:
                arg_dict = {"help": obj.cli_help}
                for attr, key in optional_attrs.items():
                    if hasattr(obj, attr) and getattr(obj, attr) is not None:
                        value = getattr(obj, attr)
                        if attr == "cli_obj_type":
                            arg_dict[key] = value.python_type
                        else:
                            arg_dict[key] = value

                if module_type == "module":
                    flags = [f"-{obj.cli_s_flag}" for obj in [obj] if obj.cli_s_flag]
                    flags.extend(
                        f"--{obj.cli_l_flag}" for obj in [obj] if obj.cli_l_flag
                    )
                else:
                    flags = []
                    if hasattr(obj, "flow") and obj.flow and module_type in obj.flow:
                        if (
                            "cli_s_flag" in obj.flow[module_type]
                            and obj.flow[module_type]["cli_s_flag"]
                        ):
                            flags.append(f"-{obj.flow[module_type]['cli_s_flag']}")
                        if (
                            "cli_l_flag" in obj.flow[module_type]
                            and obj.flow[module_type]["cli_l_flag"]
                        ):
                            flags.append(f"--{obj.flow[module_type]['cli_l_flag']}")
                    else:
                        if hasattr(obj, "cli_s_flag") and obj.cli_s_flag:
                            flags.append(f"-{obj.cli_s_flag}")
                        if hasattr(obj, "cli_l_flag") and obj.cli_l_flag:
                            flags.append(f"--{obj.cli_l_flag}")

                if flags:
                    current_group.add_argument(*flags, **arg_dict)

    # def process_miracl_objects(
    #     self, class_list: List[str], args: Dict[str, Any]
    # ) -> Dict[str, Dict[str, Any]]:
    #     """
    #     Process MiraclObj attributes and assign CLI arguments to appropriate fields.
    #
    #     This function iterates through the attributes of specified classes,
    #     matches CLI arguments to the appropriate MiraclObj attributes,
    #     and assigns values based on whether they represent file paths,
    #     directory paths, or general content.
    #
    #     :param class_list: List of class names to process
    #     :param args: Dictionary of parsed CLI arguments
    #
    #     :raises ValueError: If no matching CLI flag is found for an attribute
    #     :return: Dictionary of updated MIRACL objects
    #     """
    #     args_keys = set(args.keys())
    #     updated_miracl_objects = {class_name: {} for class_name in class_list}
    #
    #     for class_name in class_list:
    #         class_obj = globals()[class_name]
    #         for attr_name, attr_value in class_obj.__dict__.items():
    #             if isinstance(attr_value, MiraclObj):
    #                 # Initialize content as None
    #                 # This will be used to check if the content attribute has been
    #                 # assigned correctly i.e. if there is a match for the cli arg
    #                 content_matched = False
    #
    #                 cli_flag = attr_value.cli_l_flag
    #                 if cli_flag in args_keys:
    #                     arg_value = args[cli_flag]
    #                     path_type = self.check_path_type(arg_value)
    #
    #                     if hasattr(attr_value, path_type):
    #                         setattr(attr_value, path_type, arg_value)
    #                     else:
    #                         attr_value.content = arg_value
    #
    #                     content_matched = True
    #                     print(f"Attribute name: {attr_name}")
    #                     print(f"Attribute value: {attr_value}")
    #                     print(f"Assigned to: {path_type}")
    #                     print(
    #                         f"Value: {getattr(attr_value, path_type, attr_value.content)}\n"
    #                     )
    #                 else:
    #                     # If there is no match for the module flag, the assumption is
    #                     # that the module is being evoked as part of a workflow hence
    #                     # the flow attribute will be checked for a match
    #                     if (
    #                         "flow" in attr_value.__dict__
    #                         and attr_value.flow is not None
    #                     ):
    #                         flow = attr_value.flow
    #                         for _, value in flow.items():
    #                             if isinstance(value, dict) and "cli_l_flag" in value:
    #                                 flow_cli_flag = value["cli_l_flag"]
    #                                 if flow_cli_flag in args_keys:
    #                                     arg_value = args[flow_cli_flag]
    #                                     path_type = self.check_path_type(arg_value)
    #
    #                                     if hasattr(attr_value, path_type):
    #                                         setattr(attr_value, path_type, arg_value)
    #                                     else:
    #                                         attr_value.content = arg_value
    #
    #                                     content_matched = True
    #                                     print(
    #                                         f"Flow Attribute name: {attr_name} (from flow)"
    #                                     )
    #                                     print(f"Flow Attribute value: {attr_value}")
    #                                     print(f"Assigned to: {path_type}")
    #                                     print(
    #                                         f"Value: {getattr(attr_value, path_type, attr_value.content)}\n"
    #                                     )
    #                                     break
    #
    #                 # This check should technically be redundant as a match should be
    #                 # guaranteed because of how the Pydantic objects are set up and
    #                 # handled. However, I leave it in here as an additional check as
    #                 # it practially has zero overhead.
    #                 if not content_matched:
    #                     raise ValueError(
    #                         f"No matching CLI flag found for attribute '{attr_name}' in class '{class_name}'."
    #                     )
    #
    #                 updated_miracl_objects[class_name][attr_name] = attr_value
    #
    #     return updated_miracl_objects

    def process_miracl_objects(
        self, object_dict: Dict[str, Any], args: Dict[str, Any]
    ) -> None:
        """
        Process MiraclObj attributes and assign CLI arguments to appropriate fields.

        This function iterates through the attributes of specified objects,
        matches CLI arguments to the appropriate MiraclObj attributes,
        and assigns values based on whether they represent file paths,
        directory paths, or general content.

        :param object_dict: Dictionary of MIRACL objects to process
        :param args: Dictionary of parsed CLI arguments

        :raises ValueError: If no matching CLI flag is found for an attribute
        :return: Dictionary of updated MIRACL objects
        """
        args_keys = set(args.keys())

        for obj_name, class_obj in object_dict.items():
            for attr_name, attr_value in class_obj.__dict__.items():
                if isinstance(attr_value, MiraclObj):
                    # Initialize content as None
                    # This will be used to check if the content attribute has been
                    # assigned correctly i.e. if there is a match for the cli arg
                    content_matched = False

                    cli_flag = attr_value.cli_l_flag
                    if cli_flag in args_keys:
                        arg_value = args[cli_flag]
                        path_type = self.check_path_type(arg_value)

                        if hasattr(attr_value, path_type):
                            setattr(attr_value, path_type, arg_value)
                        else:
                            attr_value.content = arg_value

                        content_matched = True
                        print(f"Attribute name: {attr_name}")
                        print(f"Attribute value: {attr_value}")
                        print(f"Assigned to: {path_type}")
                        print(
                            f"Value: {getattr(attr_value, path_type, attr_value.content)}\n"
                        )
                    else:
                        # If there is no match for the module flag, the assumption is
                        # that the module is being evoked as part of a workflow hence
                        # the flow attribute will be checked for a match
                        if (
                            "flow" in attr_value.__dict__
                            and attr_value.flow is not None
                        ):
                            flow = attr_value.flow
                            for _, value in flow.items():
                                if isinstance(value, dict) and "cli_l_flag" in value:
                                    flow_cli_flag = value["cli_l_flag"]
                                    if flow_cli_flag in args_keys:
                                        arg_value = args[flow_cli_flag]
                                        path_type = self.check_path_type(arg_value)

                                        if hasattr(attr_value, path_type):
                                            setattr(attr_value, path_type, arg_value)
                                        else:
                                            attr_value.content = arg_value

                                        content_matched = True
                                        print(
                                            f"Flow Attribute name: {attr_name} (from flow)"
                                        )
                                        print(f"Flow Attribute value: {attr_value}")
                                        print(f"Assigned to: {path_type}")
                                        print(
                                            f"Value: {getattr(attr_value, path_type, attr_value.content)}\n"
                                        )
                                        break

                    # This check should technically be redundant as a match should be
                    # guaranteed because of how the Pydantic objects are set up and
                    # handled. However, I leave it in here as an additional check as
                    # it practially has zero overhead.
                    if not content_matched:
                        raise ValueError(
                            f"No matching CLI flag found for attribute '{attr_name}' in object '{obj_name}'."
                        )

    @staticmethod
    def check_path_type(path_str: str) -> str:
        """
        Check if the given path string represents a directory, file, or neither.

        :param path_str: The path string to check
        :return: 'dirpath' if it's a directory, 'filepath' if it's a file, 'content' otherwise
        """
        try:
            path = Path(path_str)
            if path.is_dir():
                return "dirpath"
            elif path.is_file():
                return "filepath"
            else:
                return "content"
        except (TypeError, ValueError):
            return "content"


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
