from miracl_datamodel import MiraclObj, ArgumentType
import argparse


def get_argparse_type(arg_type: ArgumentType):
    if arg_type == ArgumentType.STRING:
        return str
    elif arg_type == ArgumentType.INTEGER:
        return int
    elif arg_type == ArgumentType.FLOAT:
        return float
    elif arg_type == ArgumentType.BOOLEAN:
        return bool
    elif arg_type == ArgumentType.LIST:
        return list
    else:
        raise ValueError(f"Unsupported argument type: {arg_type}")


########
# MAIN #
########

fa_single = MiraclObj(
    id="cb307bde-6cbd-46b1-a044-3acd1deeb13b",
    description="Run single group for ACE flow",
    cli_name="fa_single_cli",
    cli_group="single_multi_args_group",
    tags=["ace", "flow", "main"],
    cli_s_flag="s",
    cli_l_flag="single",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to single raw tif/tiff data folder",
    cli_metavar="SINGLE_TIFF_DIR",
    gui_label="Single tif/tiff data folder",
    gui_group="main",
    gui_order=1,
    gui_widget_type="textfield",
    module="ace_flow",
    version_added="2.4.0",
)


fa_control = MiraclObj(
    id="f17b25be-abec-42af-b1c5-4f4ab3e9ffab",
    name="fa_control_cli",
    tags=["ace", "flow", "main"],
    cli_s_flag="c",
    cli_l_flag="control",
    cli_obj_type=ArgumentType.STRING,
    cli_help="FIRST: path to base control directory.\nSECOND: example path to control subject tiff directory",
    cli_metavar=("CONTROL_BASE_DIR", "CONTROL_TIFF_DIR_EXAMPLE"),
    gui_label="Base control dir",
    gui_group="main",
    gui_order=2,
    cli_nargs=2,
    version_added="2.4.0",
)


parser = argparse.ArgumentParser(description="Argument Parser from Pydantic Model")

# Add the argument to the parser
parser.add_argument(
    f"-{fa_single.cli_s_flag}",
    f"--{fa_single.cli_l_flag}",
    type=get_argparse_type(fa_single.cli_obj_type),
    metavar=fa_single.cli_metavar,
    help=fa_single.cli_help,
)

parser.add_argument(
    f"-{fa_control.cli_s_flag}",
    f"--{fa_control.cli_l_flag}",
    type=get_argparse_type(fa_control.cli_obj_type),
    metavar=fa_control.cli_metavar,
    help=fa_control.cli_help,
    nargs=fa_control.cli_nargs,
)

if __name__ == "__main__":
    args = parser.parse_args()
    args_dict = vars(args)  # Instead of dict -> Pydantic serializer
    print(type(args_dict[fa_single.cli_l_flag]))
    print(f"Value for {fa_single.cli_l_flag}: {args_dict[fa_single.cli_l_flag]}")
