from argparse import ArgumentParser
from typing import List, Dict, Union, cast, Optional


def create_parser_arguments(
    parser: ArgumentParser,
    groups_dict: Dict[str, Dict[str, Union[str, List[MiraclObj]]]],
    module_type: str = "module",
) -> None:
    """
    Create argument parser groups based on a dictionary of MiraclObj instances.

    Each group will contain command-line arguments defined by the attributes
    of the MiraclObj instances.

    :param parser: The ArgumentParser instance to which the arguments will be added.
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
    }

    for group_info in groups_dict.values():
        title = cast(str, group_info["title"])
        description = cast(
            Optional[str],
            group_info.get("description"),
        )

        current_parser = parser.add_argument_group(
            title=title,
            description=description,
        )

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
                flags.extend(f"--{obj.cli_l_flag}" for obj in [obj] if obj.cli_l_flag)
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
                current_parser.add_argument(*flags, **arg_dict)
