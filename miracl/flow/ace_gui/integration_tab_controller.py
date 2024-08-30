from PyQt5.QtWidgets import QTabWidget
from integration_tab1 import TabBuilder
from gui_factory import SectionLabel
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
from miracl.system.objs.objs_seg import SegVoxObjs as seg_vox
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace
from miracl.system.objs.objs_reg import RegClarAllenObjs as reg_clar_allen
from miracl.system.objs.objs_reg import RegWarpClarObjs as reg_warp_clar
from miracl.system.objs.objs_conv import ConvTiffNiiObjs as conv_tiff_nii


class TabController:
    def __init__(self, parent):
        """Initialize the TabController with a parent widget."""
        self.tab_widget = QTabWidget(parent)
        self.tab_obj_dicts = {}
        self.create_tabs()

    def create_tabs(self):
        """Create and add tabs to the tab widget."""
        tab1, tab1_obj_dict = TabBuilder.base_tab(
            "Main",
            [
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
        )
        tab2, tab2_obj_dict = TabBuilder.base_tab(
            "Tab 2",
            [
                SectionLabel("Test label"),
                reg_warp_clar.voxel_size,
            ],
        )

        self.tab_widget.addTab(tab1, tab1.name)
        self.tab_widget.addTab(tab2, tab2.name)

        self.tab_obj_dicts.update(tab1_obj_dict)
        self.tab_obj_dicts.update(tab2_obj_dict)

    def get_widget(self):
        """Return the tab widget for use in the main application."""
        return self.tab_widget

    def get_tab_obj_dicts(self):
        """Return the obj_dicts for each tab."""
        return self.tab_obj_dicts
