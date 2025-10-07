from miracl.system.registry.conv_template import conv_tiff_nii_dict
from miracl.system.registry.reg_template import reg_clar_allen_dict
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

# Run with defaults
reg.run("conversion")
print("")
reg.run("registration")
print("")
reg.run("generate_patch")
print("")

reg.run(
    "registration",
    overrides={
        "--output": "/tmp/from_conversion/output.nii.gz",
        "--orient_code": "LPI",
    },
)
reg.run(
    "generate_patch",
    overrides={
        "--input": "/tmp/from_conversion/output.nii.gz",
    },
)

# class_info = reg.get_info()
# for key in class_info.keys():
#     print(class_info[key]["obj_class"].__name__)
#
# print([entry["obj_class"] for entry in class_info.values()])

cli_builder = MiraclCLIBuilder(reg, module_type="ace")

parser = cli_builder.build_parser()
args, parsed_objs = cli_builder.parse()

print(f"args: {args}")
