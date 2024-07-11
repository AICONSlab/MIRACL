# ACE GUI

## Add tab

- Create `miracl_workflow_ace_gui_clusterwise_tab.py`
	- Import from `QWidget` and `QFormLayout` from `PyQt5.QtWidgets`, `WidgetUtils` from `miracl_workflow_ace_gui_widgets_utils` and `miracl_workflow_ace_parser` from `miracl.flow`
- Create `ClusterwiseTab` class including the clusterwise layout and the help dictionary created from the parser
	- Add the clusterwise widgets
- Import into `miracl_workflow_ace_gui_clusterwise_tab` into `miracl_workflow_ace_gui_tab_manager.py`
- Create flag associations with `miracl_workflow_ace_gui_flag_creator.py`
- Add clusterwise flags to `miracl_workflow_ace_gui_controller.py`
