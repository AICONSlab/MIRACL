from miracl.system.registry.conv_template import conv_tiff_nii_dict
from miracl.system.registry.reg_template import reg_clar_allen_dict
from miracl.system.registry.registry import MiraclRegistry
from miracl.system.registry.runner import default_runner

reg = MiraclRegistry()
reg.register_from_template("conversion", conv_tiff_nii_dict, default_runner)
reg.register_from_template("registration", reg_clar_allen_dict, default_runner)

# Run with defaults
reg.run("conversion")
reg.run("registration")

reg.run(
    "registration",
    overrides={
        "--output": "/tmp/from_conversion/output.nii.gz",
        "--orient_code": "LPI",
    },
)
