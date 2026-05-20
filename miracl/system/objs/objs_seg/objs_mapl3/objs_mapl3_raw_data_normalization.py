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
    ArgumentType,
    WidgetType,
)


class RawDataNormalization:
    _MRDN_GROUP = CliGroup.MAPL3_RAW_DATA_NORMALIZATION

    input_dir: MiraclObj = MiraclObj(
        name="mrdn_input_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="input tif/tiff probability map (default: None)",
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
                    s_flag="mrdn",
                    l_flag="mrdn_input",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    tiff_folder: MiraclObj = MiraclObj(
        name="mrdn_tiff_folder",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="raw_data",
            obj_type=ArgumentType.STRING,
            help="Directory containing raw .tif slices for original dimensions (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["TIFF input folder"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrdn_r",
                    l_flag="mrdn_raw_data",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    brain_mask: MiraclObj = MiraclObj(
        name="mrdn_brain_mask",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="brain_mask",
            obj_type=ArgumentType.STRING,
            help="input brain mask tif/tiff directory (default: None)",
            required=True,
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
                    s_flag="mrdn_m",
                    l_flag="mrdn_brain_mask",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    num_erosion: MiraclObj = MiraclObj(
        name="mrdn_num_erosion",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="ne",
            l_flag="num_erosion",
            obj_type=ArgumentType.INTEGER,
            help="how many times run binary erosion on the mask (default: %(default)s)",
            required=False,
            default=50,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["# of erosions"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrdn_ne",
                    l_flag="mrdn_num_erosion",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    alpha: MiraclObj = MiraclObj(
        name="mrdn_alpha",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="a",
            l_flag="num_alpha",
            obj_type=ArgumentType.FLOAT,
            help="alpha for linear mixation of probability map and raw image; 0 (only model) 1 (only raw image) (default: %(default)s)",
            required=False,
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Alpha"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=1.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrdn_a",
                    l_flag="mrdn_alpha",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    threshold: MiraclObj = MiraclObj(
        name="mrdn_threshold",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="t",
            l_flag="num_thr",
            obj_type=ArgumentType.FLOAT,
            help="threshold for binarization (default: %(default)s)",
            required=False,
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Binarization thr"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=1.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrdn_t",
                    l_flag="mrdn_thr",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="mrdn_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="Path to output directory (default: None)",
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
                    s_flag="mrdn_o",
                    l_flag="mrdn_out_dir",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mrdn_cpu_load",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="cpu_load",
            obj_type=ArgumentType.FLOAT,
            help="fraction of cpus to be used for parallelization between 0-1 (default: %(default)s)",
            required=False,
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["CPU load"],
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
                    s_flag="mrdn_c",
                    l_flag="mrdn_cpu_load",
                    group=_MRDN_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
