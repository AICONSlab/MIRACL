from typing import Dict
from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen,
)
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.datamodels.miraclobj_serializer import (
    miraclobj_to_argparse,
    should_include_in_cli,
    deserialize_parsed_args_to_objects,
)
import argparse

objs = ClarAllen
# print(dir(objs))
# print(vars(objs))
# print(objs.allen_atlas.flow["ace"]["cli_s_flag"])

parser = argparse.ArgumentParser(description="My CLI")

groups_cache = {}

for name, obj in objs.__dict__.items():
    if isinstance(obj, MiraclObj):
        if should_include_in_cli(obj, "ace"):
            flags, kwargs = miraclobj_to_argparse(obj, "ace")
            # print(f"{obj.name}: {kwargs}")

            # print("Flags:", flags)
            # print("Kwargs:", kwargs)
            # Try to get the group info from the object
            cli_group_info = None
            if obj.flow.get("ace", {}).get("cli_group") is not None:
                cli_group_info = obj.flow["ace"][
                    "cli_group"
                ].value  # expect tuple (name, description)

            if (
                cli_group_info
                and isinstance(cli_group_info, (list, tuple))
                and len(cli_group_info) >= 2
            ):
                group_name, group_desc = cli_group_info[0], cli_group_info[1]

                # Create the group only once
                if group_name not in groups_cache:
                    groups_cache[group_name] = parser.add_argument_group(
                        group_name, group_desc
                    )

                # Add this argument to the appropriate group
                groups_cache[group_name].add_argument(*flags, **kwargs)

            else:
                # No group info, just add to parser directl
                parser.add_argument(*flags, **kwargs)


args = parser.parse_args()

included_objs_list = [
    obj
    for obj in objs.__dict__.values()
    if isinstance(obj, MiraclObj) and should_include_in_cli(obj, "ace")
]

parsed_miracl_objs = deserialize_parsed_args_to_objects(
    args,
    included_objs_list,
)

for obj in parsed_miracl_objs:
    print(f"{obj.name} content: {obj.content}")

# print(args)
