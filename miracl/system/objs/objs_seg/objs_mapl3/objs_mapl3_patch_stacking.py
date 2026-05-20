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


class PatchStacking:
    _MPS_GROUP = CliGroup.MAPL3_PATCH_STACKING

    input_dir: MiraclObj = MiraclObj(
        name="mps_input_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="path to input directory containing patches (default: %(default)s)",
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
                    s_flag="mps_i",
                    l_flag="mps_input",
                    group=_MPS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="mps_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="Output directory for stitched Z-stack (default: %(default)s)",
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
                    s_flag="mps_o",
                    l_flag="mps_out_dir",
                    group=_MPS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    tiff_folder: MiraclObj = MiraclObj(
        name="mps_tiff_folder",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="raw_dir",
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
                    s_flag="mps_r",
                    l_flag="mps_raw_dir",
                    group=_MPS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mps_cpu_load",
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
            default=0.7,
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
                    s_flag="mps_c",
                    l_flag="mps_cpu_load",
                    group=_MPS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    metadata_file: MiraclObj = MiraclObj(
        name="mps_metadata",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="metadata_path",
            obj_type=ArgumentType.STRING,
            help="path to metadata JSON file (default: %(default)s)",
            required=True,
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
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mps_m",
                    l_flag="mps_metadata",
                    group=_MPS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    dtype: MiraclObj = MiraclObj(
        name="mps_dtype",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="d",
            l_flag="dtype",
            obj_type=ArgumentType.STRING,
            help="Output data type (e.g., uint16, bool; default: %(default)s)",
            default="uint16",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output data type"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mps_d",
                    l_flag="mps_dtype",
                    group=_MPS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
