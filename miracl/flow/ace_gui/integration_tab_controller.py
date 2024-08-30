from miracl import miracl_logger
from PyQt5.QtWidgets import QTabWidget, QWidget
from typing import Dict, List
from miracl_gui_tab_factory import TabBuilder
from miracl_gui_widget_factory import SectionLabel
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
from miracl.system.objs.objs_seg import SegVoxObjs as seg_vox
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace
from miracl.system.objs.objs_reg import RegClarAllenObjs as reg_clar_allen
from miracl.system.objs.objs_reg import RegWarpClarObjs as reg_warp_clar
from miracl.system.objs.objs_conv import ConvTiffNiiObjs as conv_tiff_nii

logger = miracl_logger.logger


class TabController:
    """Controller for managing tabs in a QTabWidget.

    This class initializes a QTabWidget and populates it with tabs
    based on a predefined widget dictionary. It allows for the
    retrieval of the tab widget and the associated objects for each tab.
    """

    def __init__(self, parent: QWidget) -> None:
        """Initialize the TabController with a parent widget."""
        self.tab_widget = QTabWidget(parent)
        self._tab_obj_dicts = {}  # Dict to store the widget objects
        self._tabs = []  # List to store tab objects

        # Initialize the widget_dict here
        self.widget_dict: Dict = {
            "main": [
                SectionLabel("Single or multi method arguments"),
                flow_ace.single,
                SectionLabel("Required arguments"),
                seg_ace.out_dir,
                seg_ace.model_type,
                SectionLabel("Useful/important arguments"),
                seg_ace.gpu_index,
                conv_tiff_nii.down,
                reg_clar_allen.voxel_size,
                seg_vox.downsample,
                # reg_warp_clar.voxel_size,
            ],
            "Conversion": [
                SectionLabel("Test label"),
                reg_warp_clar.voxel_size,
            ],
        }

        self.create_tabs()

    def create_tabs(self, which_tab: str = "base_tab") -> None:
        """Create tabs based on the widget_dict using the specified method from TabBuilder.

        This method iterates over the widget_dict and creates tabs in the QTabWidget.
        Each tab is associated with its corresponding objects and stored for later access.
        The method to create tabs can be specified using the `which_tab` argument,
        which defaults to "base_tab" if not provided.

        Args:
            which_tab (str): The name of the method to call from TabBuilder. Defaults to "base_tab".

        Returns:
            None
        """
        for tab_title, tab_obj_list in self.widget_dict.items():
            logger.debug(f"Processing tab: {tab_title}")
            try:
                tab_builder = getattr(TabBuilder, which_tab)
                logger.debug(f"Using tab builder method: {which_tab}")
            except AttributeError:
                error_message = f"Method '{which_tab}' does not exist in TabBuilder."
                logger.error(error_message)
                raise ValueError(error_message)

            tmp_title, tmp_obj_dict = tab_builder(
                tab_title,
                tab_obj_list,
            )
            self.tab_widget.addTab(tmp_title, tmp_title.name)
            self._tab_obj_dicts.update(tmp_obj_dict)
            self._tabs.append(tmp_title)
            logger.info("Added tab: %s", tmp_title)

    # @property
    # def tabs(self) -> List:
    #     """Get the list of tab objects."""
    #     return self._tabs
    #
    # def add_tab(self, tab_title: str, tab_obj_list: List) -> None:
    #     """Add a new tab to the controller.
    #
    #     Args:
    #         tab_title (str): The title of the tab to add.
    #         tab_obj_list (List): The list of objects associated with the tab.
    #
    #     Raises:
    #         ValueError: If the tab already exists.
    #     """
    #     if tab_title in self._tabs:
    #         raise ValueError("Tab already exists.")
    #
    #     # Create the tab using the same logic as in create_tabs
    #     tab_builder = TabBuilder.base_tab  # Assuming base_tab is the method to use
    #     tmp_title, tmp_obj_dict = tab_builder(tab_title, tab_obj_list)
    #     self.tab_widget.addTab(tmp_title, tmp_title.name)
    #     self._tab_obj_dicts.update(tmp_obj_dict)
    #     self._tabs.append(tmp_title)
    #
    # def remove_tab(self, tab_title: str) -> None:
    #     """Remove a tab from the controller.
    #
    #     Args:
    #         tab_title (str): The title of the tab to remove.
    #
    #     Raises:
    #         ValueError: If the tab is not found.
    #     """
    #     if tab_title in self._tabs:
    #         self._tabs.remove(tab_title)
    #         index = self.tab_widget.indexOf(tab_title)
    #         if index != -1:
    #             self.tab_widget.removeTab(index)
    #     else:
    #         raise ValueError("Tab not found.")

    def __str__(self) -> str:
        """Return a string representation of the TabController.

        This method returns a string that includes the current state of the
        tab_widget, including the number of tabs and their titles, as well as
        the _tab_obj_dicts and the list of tab objects.

        Returns:
            str: A formatted string representing the TabController's state,
                 including tab count, tab titles, tab object dictionaries,
                 and the list of tab objects.
        """
        tab_count = self.tab_widget.count()
        tab_titles = [self.tab_widget.tabText(i) for i in range(tab_count)]
        tab_widget_info = (
            f"Tab Widget: {tab_count} tabs - Titles: {', '.join(tab_titles)}"
        )

        tab_obj_dicts_info = f"Tab Object Dicts: {self._tab_obj_dicts}"

        tabs_info = f"Tabs: {', '.join(str(tab) for tab in self._tabs)}"

        return f"{tab_widget_info}\n{tab_obj_dicts_info}\n{tabs_info}"

    def get_widget(self) -> QTabWidget:
        """Return the tab widget for use in the main application.

        Returns:
            QTabWidget: The tab widget containing all the tabs.
        """
        return self.tab_widget

    def get_tab_obj_dicts(self) -> Dict:
        """Return the obj_dicts for each tab.

        Returns:
            Dict: A dictionary containing the objects associated with each tab.
        """
        return self._tab_obj_dicts

    def get_tabs(self) -> List:
        """Return a list of all tab objects.

        This method provides access to the list of tab objects created
        in the QTabWidget.

        Returns:
            List: A list of all tab objects.
        """
        return self._tabs
