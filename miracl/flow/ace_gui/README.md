# ACE GUI

## Add tab

- Create `miracl_workflow_ace_gui_clusterwise_tab.py`
	- Import from `QWidget` and `QFormLayout` from `PyQt5.QtWidgets`, `WidgetUtils` from `miracl_workflow_ace_gui_widgets_utils` and `miracl_workflow_ace_parser` from `miracl.flow`
- Create `ClusterwiseTab` class including the clusterwise layout and the help dictionary created from the parser
	- Add the clusterwise widgets
- Import into `miracl_workflow_ace_gui_clusterwise_tab` into `miracl_workflow_ace_gui_tab_manager.py`
- Create flag associations with `miracl_workflow_ace_gui_flag_creator.py`
- Add clusterwise flags to `miracl_workflow_ace_gui_controller.py`


- **MainWindow(QMainWindow): class** = Main PyQt5 window
    - **initialize_ui(self): def** = Initialize the UI and store widgets
    - **store_widgets(self, widget: QWidget): def** = Store the widgets in the dictionary using their object names.
    - **on_value_changed(self, name, value): def** = Handle widget value changes.
    - **load_values(self): def** = Open a dialog to load values from a JSON file.
    - **load_from_json(self, file_path: str): def** = Load settings from a JSON file and update the UI.
    - **update_widget_value(self, widget, value): def** = Update the widget with the given value.
    - **save_values(self, s_title, s_default, s_file_type): def** = Open a dialog to save values to a JSON file.
    - **get_settings_data(self) -> dict: def** = Gather data from widgets to prepare for saving.
    - **save_to_json(self, file_name: str): def** = Save settings to a JSON file.
    - **process_widget_values(self, action: str): def** = Process the values of the widgets based on the action.
    - **confirm_reset(self): def** = Show a confirmation dialog before resetting values.
    - **reset_values(self): def** = Reset values in the widgets to their default values.
    - **get_miracl_obj_by_name(self, name: str) -> MiraclObj: def** = Retrieve the MiraclObj associated with the given widget name.


- WidgetFactory Class:
    - Responsible for creating widgets based on MiraclObj instances.
    - Uses MiraclObj to determine the type of widget (dropdown, spinbox) and its default values.
    - The create_widgets_from_objects method returns both the container widget and a dictionary mapping widget names to MiraclObj instances, which simplifies accessing default values later.

- MainWindow Class:
    - Manages the main application window and handles user interactions.
    - Stores widgets in self.widgets and maps widget names to MiraclObj instances in self.miracl_objs.
    - Reset Values: Uses self.miracl_objs to reset widgets to their default values by accessing obj_default from the corresponding MiraclObj.
    - Save Values: Gathers current widget values using get_settings_data and saves them to a JSON file.
    - Load Values: Loads values from a JSON file and updates the UI, checking for unexpected or missing fields.

- Saving and Loading:
    - Saving: The save_to_json method collects current widget values and saves them along with metadata to a JSON file.
    - Loading: The load_from_json method updates widget values from a JSON file and checks for discrepancies between the file and the current UI setup.

