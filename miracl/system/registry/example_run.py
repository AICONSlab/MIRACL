from miracl.system.registry import mapl3_connectors_template
from miracl.system.registry.conv_template import conv_tiff_nii_dict
from miracl.system.registry.reg_template import reg_clar_allen_dict
from miracl.system.registry.mapl3_connectors_template import (
    mapl3_workflow_connectors_dict,
)
from miracl.system.registry.mapl3_generate_patch_template import (
    mapl3_generate_patch_dict,
)
from miracl.system.registry.registry import MiraclRegistry
from miracl.system.registry.runner import default_runner
from miracl.system.datamodels.to_argparse_class_test import MiraclCLIBuilder

reg = MiraclRegistry()
reg.register_from_template("conversion", conv_tiff_nii_dict, default_runner)
reg.register_from_template("registration", reg_clar_allen_dict, default_runner)
reg.register_from_template("generate_patch", mapl3_generate_patch_dict, default_runner)
reg.register_from_template(
    "workflow_connectors", mapl3_workflow_connectors_dict, default_runner
)

# Run with defaults
# reg.run("conversion")
# print("")
# reg.run("registration")

cli_builder = MiraclCLIBuilder(reg)

parser = cli_builder.build_parser()
args, parsed_objs = cli_builder.parse()


print("")
reg.run("conversion")
print("")
reg.run("registration")
print("")
# reg.run("generate_patch")
reg.run(
    "generate_patch",
    overrides={
        "--mgp_input": "/tmp/from_conversion/output.nii.gz",
    },
)
print("")

# reg.run(
#     "conversion",
#     overrides={
#
#     }
# )


# reg.run(
#     "registration",
#     overrides={
#         "--output": "/tmp/from_conversion/output.nii.gz",
#         "--orient_code": "LPI",
#     },
# )

# class_info = reg.get_info()
# for key in class_info.keys():
#     print(class_info[key]["obj_class"].__name__)
#
# print([entry["obj_class"] for entry in class_info.values()])

# cli_builder = MiraclCLIBuilder(reg)
#
# parser = cli_builder.build_parser()
# args, parsed_objs = cli_builder.parse()
#
print(f"args: {args}")
print("")

obj_class = reg.get_class("conversion")
# print(obj_class)

attr_instance = getattr(obj_class, "tiff_folder")

test_flag = attr_instance.flow.get("mapl3", {}).get("cli_l_flag")

test_value = getattr(
    reg.get_class("workflow_connectors"), "mapl3_workflow_raw_tiff_folder"
).content

print(f"FLAG: {test_flag}")
print(f"VALUE: {test_value}")

print("")
reg.run(
    "conversion",
    overrides={
        f"--{test_flag}": test_value,
    },
)
print("")

# NOTE: Something like reg.override_flag("conversion", "tiff_folder") and
# reg.override_content("workflow_connectors", "mapl3_workflow_raw_tiff_folder")
