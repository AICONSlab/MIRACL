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


class Skeletonization:
    _MS_GROUP = CliGroup.MAPL3_SKELETONIZATION

    input_dir: MiraclObj = MiraclObj(
        name="ms_input_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="input tif/tiff probability map (default: %(default)s)",
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
                    s_flag="ms",
                    l_flag="ms_input",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    brain_mask: MiraclObj = MiraclObj(
        name="ms_brain_mask",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="brain_mask",
            obj_type=ArgumentType.STRING,
            help="input brain mask tif/tiff directory (default: %(default)s)",
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
                    s_flag="ms_m",
                    l_flag="ms_brain_mask",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    threshold: MiraclObj = MiraclObj(
        name="ms_threshold",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="t",
            l_flag="threshold",
            obj_type=ArgumentType.INTEGER,
            help="threshold for skipping analysis based on the number of forground in mask (default: %(default)s)",
            required=False,
            default=1000,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Skipping analysis thr"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0,
                        max_val=100_000,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_t",
                    l_flag="ms_threshold",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    num_erosion: MiraclObj = MiraclObj(
        name="ms_num_erosion",
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
                        max_val=10_000,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_ne",
                    l_flag="ms_num_erosion",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="ms_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="Path to output directory (default: %(default)s)",
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
                    s_flag="ms_o",
                    l_flag="ms_out_dir",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    remove_small_obj_thr: MiraclObj = MiraclObj(
        name="ms_remove_small_obj_thr",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="ts",
            l_flag="remove_small_obj_thr",
            obj_type=ArgumentType.INTEGER,
            help="thr (number of voxels) for removing small object (default: %(default)s)",
            required=False,
            default=64,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Remove small obj thr"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=100_000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_ts",
                    l_flag="ms_remove_small_obj_thr",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    remove_large_obj_thr: MiraclObj = MiraclObj(
        name="ms_remove_large_obj_thr",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="tl",
            l_flag="remove_large_obj_thr",
            obj_type=ArgumentType.INTEGER,
            help="thr (number of voxels) for removing large object (default: %(default)s)",
            required=False,
            default=50_000,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Remove large obj thr"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=1_000_000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_tl",
                    l_flag="ms_remove_large_obj_thr",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    elongation_thr: MiraclObj = MiraclObj(
        name="ms_elongation_thr",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="e",
            l_flag="elongation_thr",
            obj_type=ArgumentType.INTEGER,
            help="elongation threshold of an object (number of voxels) for removing large object (default: %(default)s)",
            required=False,
            default=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Elongation thr"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10_000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_e",
                    l_flag="ms_elongation_thr",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    euler_number_thr: MiraclObj = MiraclObj(
        name="ms_euler_number_thr",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="eu",
            l_flag="euler_number_thr",
            obj_type=ArgumentType.INTEGER,
            help="number of holes allowed an object has (default: %(default)s)",
            required=False,
            default=100,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Euler number thr"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10_000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_eu",
                    l_flag="ms_euler_number_thr",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load: MiraclObj = MiraclObj(
        name="ms_cpu_load",
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
                    s_flag="ms_c",
                    l_flag="ms_cpu_load",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    dilate_distance_transform_flag: MiraclObj = MiraclObj(
        name="dilate_distance_transform_flag",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="d",
            l_flag="dilate_distance_transform_flag",
            obj_type=ArgumentType.BOOLEAN,
            help="whether to dilate distance transform (default: %(default)s)",
            required=False,
            default=True,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Dilate distance transform"],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["Yes", "No"],
                        default_val="Yes",
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="ms_d",
                    l_flag="ms_dilate_distance_transform_flag",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    tiff_folder: MiraclObj = MiraclObj(
        name="ms_raw_data",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="raw_data",
            obj_type=ArgumentType.STRING,
            help="Directory containing raw .tif slices for original dimensions (default: %(default)s)",
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
                    s_flag="ms_r",
                    l_flag="ms_raw_data",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    alpha: MiraclObj = MiraclObj(
        name="ms_alpha",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="a",
            l_flag="alpha",
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
                        min_val=0.0,
                        max_val=1.0,
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
                    s_flag="ms_a",
                    l_flag="ms_alpha",
                    group=_MS_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
