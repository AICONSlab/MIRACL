from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)


class FlowAceObjs:
    single = MiraclObj(
        id="cb307bde-6cbd-46b1-a044-3acd1deeb13b",
        description="Run single group for ACE flow",
        name="fa_single",
        tags=["ace", "flow", "ace_flow"],
        cli_s_flag="s",
        cli_l_flag="single",
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to single raw tif/tiff data folder",
        cli_metavar="SINGLE_TIFF_DIR",
        gui_label=["Single tif/tiff data folder"],
        gui_group={"ace_flow": "main"},
        gui_order=[1],
        module="ace",
        module_group="flow",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    control = MiraclObj(
        id="f17b25be-abec-42af-b1c5-4f4ab3e9ffab",
        name="fa_control",
        tags=["ace", "flow", "ace_flow"],
        cli_s_flag="c",
        cli_l_flag="control",
        cli_obj_type=ArgumentType.STRING,
        cli_help="FIRST: path to base control directory.\nSECOND: example path to control subject tiff directory",
        cli_metavar=("CONTROL_BASE_DIR", "CONTROL_TIFF_DIR_EXAMPLE"),
        gui_label=["Base control dir", "Base control tif/tiff dir"],
        gui_group={"ace_flow": "main"},
        gui_order=[2],
        cli_nargs=2,
        module="ace",
        module_group="flow",
        version_added="2.4.0",
    )

    treated = MiraclObj(
        id="911bdad2-0359-445d-bc7c-a41257ee1a30",
        name="fa_treated",
        tags=["ace", "flow", "ace_flow"],
        cli_s_flag="t",
        cli_l_flag="treated",
        cli_obj_type=ArgumentType.STRING,
        cli_help="FIRST: path to base treated directory.\nSECOND: example path to treated subject tiff directory",
        cli_metavar=("TREATED_BASE_DIR", "TREATED_TIFF_DIR_EXAMPLE"),
        gui_label=["Base treated dir", "Base treated tif/tiff dir"],
        gui_group={"ace_flow": "main"},
        gui_order=[3.1, 3.2],
        cli_nargs=2,
        module="ace",
        module_group="flow",
        version_added="2.4.0",
    )
    rerun_registration = MiraclObj(
        id="4f0b36ff-b51c-4168-a109-65b516088147",
        name="fa_rerun_registration",
        tags=["ace", "flow", "ace_flow"],
        cli_l_flag="rerun-registration",
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="whether to rerun registration step of flow; True => Force re-run (default: %(default)s)",
        cli_metavar=("TRUE/FALSE",),
        gui_group={"ace_flow": "main"},
        gui_label=["Rerun registration"],
        version_added="2.4.0",
        module="ace",
        module_group="flow",
        obj_default=False,
        gui_choice_override={
            "vals": ["yes", "no"],
            "default_val": "no",
        },
    )

    rerun_segmentation = MiraclObj(
        id="a73230bf-d291-4fb6-8f8b-becae5db2b96",
        name="fa_rerun_segmentation",
        tags=["ace", "flow", "ace_flow"],
        cli_l_flag="rerun-segmentation",
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="whether to rerun segmentation step of flow; True => Force re-run (default: %(default)s)",
        cli_metavar=("TRUE/FALSE",),
        gui_group={"ace_flow": "main"},
        gui_label=["Rerun segmentation"],
        version_added="2.4.0",
        module="ace",
        module_group="flow",
        obj_default=False,
        gui_choice_override={
            "vals": ["yes", "no"],
            "default_val": "no",
        },
    )

    rerun_conversion = MiraclObj(
        id="ecd4878f-c115-498b-8683-0dfa88d375aa",
        name="fa_rerun_conversion",
        cli_l_flag="rerun-conversion",
        tags=["ace", "flow", "ace_flow"],
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="whether to rerun conversion step of flow; True => Force re-run (default: %(default)s)",
        cli_metavar=("TRUE/FALSE",),
        gui_group={"ace_flow": "main"},
        gui_label=["Rerun conversion"],
        version_added="2.4.0",
        module="ace",
        module_group="flow",
        obj_default=False,
        gui_choice_override={
            "vals": ["yes", "no"],
            "default_val": "no",
        },
    )
