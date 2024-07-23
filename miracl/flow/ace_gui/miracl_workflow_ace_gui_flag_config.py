from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser
from typing import Dict, Any, Union


class FlagConfig:
    def __init__(self) -> None:
        """
        Initializes the FlagConfig instance and extracts option values from
        argparser into a dictionary.
        """
        self.flag_dict: Dict[str, Any] = wu.extract_arguments_to_dict_2(
            miracl_workflow_ace_parser.ACEWorkflowParser()
        )

    def create_conversion(self) -> Dict[str, Dict[str, str]]:
        """
        Creates a dictionary for the conversion module that includes all
        flags.

        :return: A dictionary containing conversion information.
        """
        conversion_dict: Dict[str, Dict[str, str]] = {
            "conv_channum": self.add_to_nested_dict(
                self.flag_dict["ctn_channum"],
                label="Channel #",
                widget_type="textfield",
            ),
            "conv_chanprefix": self.add_to_nested_dict(
                self.flag_dict["ctn_chanprefix"],
                label="Channel prefix",
                validator="alphanumeric",
                widget_type="textfield",
            ),
            "conv_chanoutname": self.add_to_nested_dict(
                self.flag_dict["ctn_channame"],
                label="Output channel name",
                validator="alphanumeric",
                widget_type="textfield",
            ),
            "conv_outnii": self.add_to_nested_dict(
                self.flag_dict["ctn_outnii"],
                label="Out nii name",
                validator="alphanumeric",
                widget_type="textfield",
            ),
            "conv_center": self.add_to_nested_dict(
                self.flag_dict["ctn_center"],
                label="Nii center",
            ),
            "conv_downzdim": self.add_to_nested_dict(
                self.flag_dict["ctn_downzdim"],
                label="Z-axis dx",
                widget_type="spinbox",
            ),
            "conv_prevdown": self.add_to_nested_dict(
                self.flag_dict["ctn_prevdown"],
                label="Previous dx",
                widget_type="spinbox",
            ),
            "conv_percentilethr": self.add_to_nested_dict(
                self.flag_dict["ctn_percentile_thr"],
                label="% threshold intensity corr",
                widget_type="textfield",
            ),
        }

        return conversion_dict

    def create_clusterwise(self) -> Dict[str, Dict[str, str]]:
        """
        Creates a dictionary for the clusterwise module that includes all
        flags.

        :return: A dictionary containing clusterwise information.
        """
        clusterwise_dict: Dict[str, Dict[str, str]] = {
            "clust_atlasdir": self.add_to_nested_dict(
                self.flag_dict["pcs_atlas_dir"],
                label="Path to atlas dir",
                widget_type="textfield",
            ),
            "clust_numperm": self.add_to_nested_dict(
                self.flag_dict["pcs_num_perm"],
                label="# permutations",
                widget_type="textfield",
            ),
            "clust_imgresolution": self.add_to_nested_dict(
                self.flag_dict["pcs_img_resolution"],
                label="Resolution of images (um)",
                widget_type="multiplechoice",
            ),
            "clust_smoothingfwhm": self.add_to_nested_dict(
                self.flag_dict["pcs_smoothing_fwhm"],
                label="fwhm of Gaussian kernel (px)",
                widget_type="textfield",
            ),
            "clust_tfcestart": self.add_to_nested_dict(
                self.flag_dict["pcs_tfce_start"],
                label="tfce threshold start",
                widget_type="textfield",
            ),
            "clust_tfcestep": self.add_to_nested_dict(
                self.flag_dict["pcs_tfce_step"],
                label="tfce threshold step",
                widget_type="textfield",
            ),
            "clust_cpuload": self.add_to_nested_dict(
                self.flag_dict["pcs_cpu_load"],
                label="% CPU's for parallelization",
                widget_type="textfield",
                min_val=0.00,
                max_val=1.00,
                increment_val=0.01,
                nr_decimals=2,
            ),
            "clust_tfceh": self.add_to_nested_dict(
                self.flag_dict["pcs_tfce_h"],
                label="tfce H power",
                widget_type="textfield",
            ),
            "clust_tfcee": self.add_to_nested_dict(
                self.flag_dict["pcs_tfce_e"],
                label="tfce E power",
                widget_type="textfield",
            ),
            "clust_stepdownp": self.add_to_nested_dict(
                self.flag_dict["pcs_step_down_p"],
                label="Step down p-value",
                widget_type="textfield",
                min_val=0.0000,
                max_val=1.0000,
                increment_val=0.01,
                nr_decimals=4,
            ),
            "clust_maskthr": self.add_to_nested_dict(
                self.flag_dict["pcs_mask_thr"],
                label="% for binarizing mean diff",
                widget_type="textfield",
                min_val=0,
                max_val=100,
                increment_val=1,
            ),
        }

        return clusterwise_dict

    @staticmethod
    def add_to_nested_dict(
        nested_dict: Dict[str, Any],
        label: str = "",
        validator: str = "",
        widget_type: str = "",
        min_val: Union[int, float, None] = None,
        max_val: Union[int, float, None] = None,
        increment_val: Union[int, float, None] = None,
        nr_decimals: Union[int, None] = None,
    ) -> Dict[str, Any]:
        """
        Adds additional key/value pairs to nested dictionary.
        If no values are provided, they are initialized to empty strings.

        :param nested_dict: The nested dictionary to update.
        :param label: The value for the 'label' key. Defaults to an empty string.
        :param validator: The value for the 'validator' key. Defaults to an empty string.
        :return: The updated nested dictionary with 'label' and 'validator' keys.
        """
        nested_dict["label"] = label
        nested_dict["validator"] = validator
        nested_dict["widget_type"] = widget_type
        nested_dict["min_val"] = min_val
        nested_dict["max_val"] = max_val
        nested_dict["increment_val"] = increment_val
        nested_dict["nr_decimals"] = nr_decimals
        return nested_dict  # Return the updated dictionary
