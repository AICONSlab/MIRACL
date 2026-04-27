from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiWidgetSpecifics,
    RangeFormConfig,
    GuiDelta,
    FlowOverride,
    ArgumentSource,
    GuiChoiceOverrideConfig,
    ArgumentType,
    WidgetType,
)


class Inference:
    _MI_GROUP = CliGroup.MAPL3_INFERENCE

    config: MiraclObj = MiraclObj(
        name="mi_config",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="config",
            obj_type=ArgumentType.STRING,
            help="path of config file used during training to define the model",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Config file"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mi_c",
                    l_flag="mi_config",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="mi_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="output_path",
            obj_type=ArgumentType.STRING,
            help="path of output directory (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output directory"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mi_o",
                    l_flag="mi_out_dir",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    model_path: MiraclObj = MiraclObj(
        name="mi_model_path",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="model_path",
            obj_type=ArgumentType.STRING,
            help="path to trained model",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Path to trained model"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mi_m",
                    l_flag="mi_model_path",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    input_dir: MiraclObj = MiraclObj(
        name="mi_input_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input_dir",
            obj_type=ArgumentType.STRING,
            help="path to input directory containing patches (default: $(default)s)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Input directory"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mi_i",
                    l_flag="mi_input_dir",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    gpu_index: MiraclObj = MiraclObj(
        name="mi_gpu_index",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="g",
            l_flag="gpu_index",
            obj_type=ArgumentType.STRING,
            help="gpu index to be used; if you wanna use all the available gpus, pass 'all' as the flag argument (default: %(default)s)",
            required=False,
            default="0",
            choices=[str(i) for i in range(11)] + ["all"],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["GPU index"],
                widget_type=WidgetType.COMBO_BOX,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mi_g",
                    l_flag="mi_gpu_index",
                    group=_MI_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    binarization_threshold: MiraclObj = MiraclObj(
        name="mi_binarization_threshold",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="b",
            l_flag="binarization_threshold",
            obj_type=ArgumentType.FLOAT,
            help="threshold (between 0-1) to binarize the model probabilty map (default: %(default)s)",
            required=False,
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Tissue % threshold"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.0,
                        max_val=1.0,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mi_b",
                    l_flag="mi_binarization_threshold",
                    group=_MI_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    save_prob_map: MiraclObj = MiraclObj(
        name="mi_save_prob_map_flag",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="s",
            l_flag="save_prob_map_flag",
            obj_type=ArgumentType.CUSTOM_BOOL,
            help="set to save prob map (default: %(default)s)",
            required=False,
            default=False,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Save prob map"],
                widget_type=WidgetType.COMBO_BOX,
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
                    s_flag="mi_s",
                    l_flag="mi_save_prob_map_flag",
                    group=_MI_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    metadata_file: MiraclObj = MiraclObj(
        name="mi_metadata",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="j",
            l_flag="metadata",
            obj_type=ArgumentType.STRING,
            help="path to metadata JSON file (default: %(default)s)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Path to metadata JSON"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mi_j",
                    l_flag="mi_metadata",
                    group=_MI_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    tissue_percentage_threshold: MiraclObj = MiraclObj(
        name="mi_tissue_percentage_threshold",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="p",
            l_flag="tissue_percentage_threshold",
            obj_type=ArgumentType.FLOAT,
            help="threshold between 0-100 to filter empty patches (default: %(default)s)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Tissue % threshold"],
                widget_type=WidgetType.NULLABLE_DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.0,
                        max_val=100.0,
                        increment_val=0.1,
                        nr_decimals=1,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mi_p",
                    l_flag="mi_tissue_percentage_threshold",
                    group=_MI_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
