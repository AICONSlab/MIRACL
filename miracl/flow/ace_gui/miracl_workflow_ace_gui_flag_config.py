from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser
from typing import Dict, Any


class FlagConfig:
    def __init__(self) -> None:
        """
        Initializes the FlagConfig instance and extracts arguments into a dictionary.
        """
        self.flag_dict: Dict[str, Any] = wu.extract_arguments_to_dict_2(
            miracl_workflow_ace_parser.ACEWorkflowParser()
        )

    def create_conversion(self) -> Dict[str, Dict[str, str]]:
        """
        Creates a conversion dictionary that includes channel number information.

        :return: A dictionary containing conversion information, including 'conv_channum'.
        """
        conversion_dict: Dict[str, Dict[str, str]] = {
            "conv_channum": self.add_to_nested_dict(
                self.flag_dict["ctn_channum"], label="Channel #:"
            ),
            "conv_chanprefix": self.add_to_nested_dict(
                self.flag_dict["ctn_chanprefix"],
                label="Channel prefix:",
                validator="alphanumeric",
            ),
            "conv_chanoutname": self.add_to_nested_dict(
                self.flag_dict["ctn_channame"],
                label="Output channel name:",
                validator="alphanumeric"
                )
        }

        return conversion_dict

    @staticmethod
    def add_to_nested_dict(
        nested_dict: Dict[str, Any], label: str = "", validator: str = ""
    ) -> Dict[str, Any]:
        """
        Adds 'label' and 'validator' key-value pairs to the nested dictionary.
        If no values are provided, they are initialized to empty strings.

        :param nested_dict: The nested dictionary to update.
        :param label: The value for the 'label' key. Defaults to an empty string.
        :param validator: The value for the 'validator' key. Defaults to an empty string.
        :return: The updated nested dictionary with 'label' and 'validator' keys.
        """
        nested_dict["label"] = label
        nested_dict["validator"] = validator
        return nested_dict  # Return the updated dictionary
