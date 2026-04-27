from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    GuiChoiceOverrideConfig,
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    FlowOverride,
    ArgumentSource,
    ArgumentType,
    RangeFormConfig,
    WidgetType,
    GuiWidgetSpecifics,
)


class GeneratePatch:
    _GP_GROUP = CliGroup.MAPL3_GENERATE_PATCH

    input: MiraclObj = MiraclObj(
        name="mgp_input",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="input directory containing .tiff or .tif slices (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Input folder"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mgp_i",
                    l_flag="mgp_input",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    brain_mask: MiraclObj = MiraclObj(
        name="mgp_brain_mask",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="brain_mask",
            obj_type=ArgumentType.STRING,
            help="input directory containing .tiff or .tif brain mask slices if not passed it will compute mask (default: %(default)s)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Brain mask"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mgp_m",
                    l_flag="mgp_brain_mask",
                    group=_GP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="mgp_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="output directory for patches (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output directory for patches"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mgp_o",
                    l_flag="mgp_out_dir",
                    group=CliGroup.REQUIRED,
                    required=True,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mgp_cpu_load",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="cpu_load",
            obj_type=ArgumentType.FLOAT,
            help="fraction of cpus to be used for parallelization. Value needs to be between 0-1 (default: %(default)s)",
            required=False,
            default=0.7,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["CPU load"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=1.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
                order=3.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mgp_c",
                    l_flag="mgp_cpu_load",
                    group=_GP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    patch_size: MiraclObj = MiraclObj(
        name="mgp_patch_size",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="p",
            l_flag="patch_size",
            obj_type=ArgumentType.INTEGER,
            help="the outputs will be patch size x patch size x patch size (ZxYxX; default: %(default)s)",
            required=False,
            default=256,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Patch size"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
                order=4.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mgp_p",
                    l_flag="mgp_patch_size",
                    group=_GP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    brain_mask_erosion: MiraclObj = MiraclObj(
        name="mgp_brain_mask_erosion_flag",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="e",
            l_flag="brain_mask_erosion_flag",
            obj_type=ArgumentType.CUSTOM_BOOL,
            help="set if you want to erode the brain mask (default: %(default)s)",
            required=False,
            choices=[True, False],
            default=False,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Erode brain mask"],
                widget_type=WidgetType.COMBO_BOX,
                order=5.0,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["Yes", "No"],
                        default_val="No",
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mgp_e",
                    l_flag="mgp_brain_mask_erosion_flag",
                    group=_GP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
