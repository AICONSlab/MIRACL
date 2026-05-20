"""
pyqt5_learning_builder.py
=========================

A bare-minimum PyQt5 window built entirely from first principles.

PURPOSE
-------
This script teaches the core mechanics of a GUI builder WITHOUT any schema,
serializer, or MIRACL infrastructure. Every widget is created manually, every
connection is wired manually, and every value is collected manually. This is
exactly what the final MiraclPyQtGuiBuilder does automatically — but here
you can see every step happening explicitly.

Once you are comfortable with what this script does, the production builder
will be much easier to read because you will recognise each part.

HOW TO RUN
----------
    python pyqt5_learning_builder.py

When you click Run, the collected values are printed to the console.

WHAT THIS SCRIPT COVERS
-----------------------
  1. The Qt application and event loop
  2. Widgets:  QSpinBox, QLineEdit, QCheckBox, QComboBox
  3. Layouts:  QFormLayout, QVBoxLayout, QHBoxLayout
  4. Signals and slots (the Qt connection model)
  5. Collecting values from widgets
  6. The UUID-keyed result dict — the contract with the deserializer
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import sys

# PyQt5 is split into sub-modules.
#   QtWidgets  — all visible UI elements (windows, buttons, labels, inputs)
#   QtCore     — non-visual Qt machinery (signals, event loop constants)
#   QtGui      — graphics helpers (validators, fonts, icons)
from PyQt5 import QtWidgets, QtCore, QtGui


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — THE QApplication
# ─────────────────────────────────────────────────────────────────────────────
#
# Every Qt program needs exactly one QApplication object. It owns the event
# loop — the invisible engine that waits for user input (mouse clicks,
# keystrokes) and dispatches those events to the right widget.
#
# sys.argv is passed in because Qt can consume certain command-line flags
# (e.g. display settings on Linux). Passing it in is the correct habit even
# when you don't use any flags yourself.
#
# Rule: create QApplication BEFORE creating any widgets. Qt will crash or
# behave unexpectedly if you create a widget first.

app = QtWidgets.QApplication(sys.argv)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — THE TOP-LEVEL WINDOW (QDialog)
# ─────────────────────────────────────────────────────────────────────────────
#
# We use QDialog rather than QMainWindow because QDialog is designed for
# exactly this use case: a temporary window that collects input and returns
# a result. QMainWindow is for full application windows with menus, toolbars,
# and status bars — overkill here.
#
# QDialog has two built-in return codes:
#   QDialog.Accepted  — user confirmed (Run button)
#   QDialog.Rejected  — user cancelled (Cancel button or closed window)
#
# We will use these in Step 7.

dialog = QtWidgets.QDialog()
dialog.setWindowTitle("MIRACL — Learning Builder")
dialog.setMinimumWidth(500)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — LAYOUTS
# ─────────────────────────────────────────────────────────────────────────────
#
# In Qt, you never set pixel positions for widgets directly (unlike what you
# may have done in some C++ desktop frameworks). Instead, you use LAYOUTS —
# objects that automatically arrange their child widgets.
#
# The three layouts you will use most:
#
#   QVBoxLayout  — stacks children VERTICALLY, one below the other
#   QHBoxLayout  — arranges children HORIZONTALLY, side by side
#   QFormLayout  — two-column grid: left column = labels, right = widgets
#                  This is the standard layout for settings dialogs.
#
# Here we create a root QVBoxLayout and attach it to the dialog. Everything
# else we add will be stacked vertically inside this root layout.
#
# setSpacing(10)      — 10px gap between each item in the layout
# setContentsMargins  — padding inside the layout's edges (left, top, right, bottom)

root_layout = QtWidgets.QVBoxLayout(dialog)
root_layout.setSpacing(10)
root_layout.setContentsMargins(16, 16, 16, 16)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — A TITLE LABEL
# ─────────────────────────────────────────────────────────────────────────────
#
# QLabel displays static text. It is not interactive — it just shows text.
# We use one here as a visual title for the form.
#
# setText() accepts plain text or a small subset of HTML. The <b> tag makes
# the text bold. Qt calls this "rich text" mode and it is enabled
# automatically when Qt detects HTML tags in the string.

title_label = QtWidgets.QLabel("<b>Workflow Configuration</b>")
root_layout.addWidget(title_label)

# addWidget() is how you place a widget inside a layout. The layout takes
# ownership and manages the widget's position and size from this point on.


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — THE FORM LAYOUT AND THE FOUR WIDGETS
# ─────────────────────────────────────────────────────────────────────────────
#
# We nest a QFormLayout inside the root QVBoxLayout. This is the two-column
# label/widget grid that displays each argument as a row.
#
# In the production builder, this loop happens automatically by iterating
# over schema.tabs[tab_key].args. Here, we do it manually for four arguments
# so every step is visible.

form_layout = QtWidgets.QFormLayout()
form_layout.setLabelAlignment(QtCore.Qt.AlignRight)  # labels right-aligned
form_layout.setVerticalSpacing(8)
form_layout.setHorizontalSpacing(16)
root_layout.addLayout(form_layout)

# addLayout() is like addWidget() but for nesting one layout inside another.


# ── Widget 1: QSpinBox ───────────────────────────────────────────────────────
#
# QSpinBox is an integer input with up/down arrows. It enforces a numeric
# range and never lets the user type an invalid value.
#
# In the production builder this is created by _make_spinbox() and driven
# by GuiFieldSpec.props.range (min_val, max_val, increment_val).
# Here we set those values manually so you can see what _make_spinbox() does.
#
# The UUID below is what the production builder uses as the dict key.
# In the real system it comes from str(resolved.id) — a UUID that uniquely
# identifies this argument across the entire registry.
# Here we just hard-code a fake UUID so the output looks realistic.

UUID_DOWNSAMPLING = "uuid-0001-downsampling-factor"

spinbox = QtWidgets.QSpinBox()
spinbox.setMinimum(1)  # from GuiRangeProps.min_val
spinbox.setMaximum(16)  # from GuiRangeProps.max_val
spinbox.setSingleStep(1)  # from GuiRangeProps.increment_val
spinbox.setValue(4)  # from GuiFieldSpec.default  (cast to int)
spinbox.setSuffix("x")  # from spec.extensions["qt"]["suffix"]

# addRow() adds one label/widget pair to the QFormLayout.
# The label text here comes from GuiFieldSpec.label[0] in the real builder.
form_layout.addRow("Downsampling factor:", spinbox)


# ── Widget 2: QLineEdit ──────────────────────────────────────────────────────
#
# QLineEdit is a single-line text input — the most basic input widget.
# In the production builder it handles string arguments, but also PATH_INPUT
# (where it is paired with a Browse button — we'll keep it simple here).
#
# setPlaceholderText() shows grey hint text when the field is empty.
# This comes from spec.extensions["qt"]["placeholder"] in the real builder.
#
# QIntValidator restricts input to integers only. In the real builder this
# comes from GuiTextProps.input_restrictions == "INTEGERS_ONLY".

UUID_OUTPUT_DIR = "uuid-0002-output-directory"

line_edit = QtWidgets.QLineEdit()
line_edit.setPlaceholderText("/path/to/output")  # from qt extensions
line_edit.setText("")  # from GuiFieldSpec.default

form_layout.addRow("Output directory:", line_edit)


# ── Widget 3: QCheckBox ──────────────────────────────────────────────────────
#
# QCheckBox is a boolean toggle. isChecked() returns True or False.
# In the production builder the initial state comes from bool(spec.default).
#
# Notice: we pass an EMPTY string as the label to addRow() here.
# That is because QCheckBox already has its own text label built in
# (set via QCheckBox("label text")). Using both would double-up the label.

UUID_SAVE_INTERMEDIATE = "uuid-0003-save-intermediate"

checkbox = QtWidgets.QCheckBox("Save intermediate files")
checkbox.setChecked(False)  # from bool(GuiFieldSpec.default)

form_layout.addRow("", checkbox)


# ── Widget 4: QComboBox ──────────────────────────────────────────────────────
#
# QComboBox is a drop-down selector. Each item has:
#   - a DISPLAY LABEL  (what the user sees)
#   - a DATA VALUE     (what gets collected into the result dict)
#
# addItem(label, data) stores both. itemData(index) retrieves the data value.
# This separation is important: the user might see "High quality (slow)"
# but the underlying value stored is "hq". In the real builder, display
# labels come from spec.props.choices.vals and data values from spec.choices.

UUID_REGISTRATION_TYPE = "uuid-0004-registration-type"

combo = QtWidgets.QComboBox()

# addItem(display_label, data_value)
# In the production builder: display_label = spec.props.choices.vals[i]
#                            data_value    = spec.choices[i]
combo.addItem("Affine", "affine")
combo.addItem("Rigid", "rigid")
combo.addItem("Deformable (SyN)", "syn")

# Select the default by matching the data value, not the display label.
# In the real builder: spec.default contains the data value.
# findData() scans item data and returns the matching index, or -1.
default_value = "affine"
default_index = combo.findData(default_value)
if default_index >= 0:
    combo.setCurrentIndex(default_index)

form_layout.addRow("Registration type:", combo)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — SIGNALS AND SLOTS
# ─────────────────────────────────────────────────────────────────────────────
#
# Qt's signal/slot system is how widgets communicate. A SIGNAL is an event
# that a widget emits when something happens (e.g. the user changed a value).
# A SLOT is a function that gets called when that signal fires.
#
# You connect them with:
#   widget.someSignal.connect(some_function)
#
# From your C++ experience: it is the same concept, just without the
# Q_OBJECT macro or explicit emit keyword — Python handles those automatically.
#
# Here is a simple example: we print a message whenever the spinbox value
# changes. In the production builder, this same mechanism is used by
# _wire_dependencies() to enable/disable widgets based on other widgets'
# values.
#
# The signal valueChanged carries the new integer value as an argument.
# We ignore it here with _ (we don't need it for this demo).


def on_downsampling_changed(new_value: int) -> None:
    """
    This function is a SLOT — it is called automatically by Qt whenever
    the spinbox value changes. The integer argument is the new value.

    In the production builder, the equivalent slot is _update_states(),
    which re-evaluates the enabled/disabled state of every widget that
    has a depends_on or conflicts_with relationship.
    """
    print(f"[signal] Downsampling changed to: {new_value}")


# connect() registers the slot. From this point on, every time the user
# changes the spinbox, Qt calls on_downsampling_changed automatically.
spinbox.valueChanged.connect(on_downsampling_changed)

# Common signals by widget type (you will use these in the production builder):
#
#   QSpinBox / QDoubleSpinBox  ->  valueChanged(int / float)
#   QLineEdit                  ->  textChanged(str)
#   QCheckBox                  ->  stateChanged(int)  — 0=unchecked, 2=checked
#   QComboBox                  ->  currentIndexChanged(int)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — THE RUN AND CANCEL BUTTONS
# ─────────────────────────────────────────────────────────────────────────────
#
# Buttons live in a horizontal row at the bottom of the dialog.
# We use QHBoxLayout to place them side by side.
#
# addStretch() inserts an invisible expanding spacer. Without it, the buttons
# would appear at the left edge. With it, the spacer pushes them to the right.

button_row = QtWidgets.QWidget()
button_layout = QtWidgets.QHBoxLayout(button_row)
button_layout.setContentsMargins(0, 0, 0, 0)

button_layout.addStretch()  # pushes buttons to the right

cancel_button = QtWidgets.QPushButton("Cancel")
run_button = QtWidgets.QPushButton("Run")

# setDefault(True) makes Run respond to the Enter key
run_button.setDefault(True)

button_layout.addWidget(cancel_button)
button_layout.addWidget(run_button)
root_layout.addWidget(button_row)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 — COLLECTING VALUES AND THE RESULT DICT
# ───────────────────────────────────────────────────â─────────────────────────
#
# When the user clicks Run, we read the current value out of every widget
# and store it in a dict keyed by the argument's UUID string.
#
# This dict is EXACTLY what the production builder's collect_results()
# produces and EXACTLY what deserialize_parsed_args_to_objects() expects.
# The only difference is that the production builder also coerces types
# (e.g. int(raw_value)) and includes hidden INTERNAL arguments.
#
# Notice: combo.itemData(combo.currentIndex()) — not combo.currentText().
# currentText() gives the display label ("Affine"). itemData() gives the
# underlying data value ("affine"). The deserializer needs the data value.


def on_run_clicked() -> None:
    """
    Slot called when the user clicks Run.

    In the production builder this is _on_run_clicked(), which calls
    _collect_results() and then dialog.accept() on success.
    """

    # ── Collect raw values from each widget ──────────────────────────────
    result = {
        UUID_DOWNSAMPLING: spinbox.value(),
        UUID_OUTPUT_DIR: line_edit.text(),
        UUID_SAVE_INTERMEDIATE: checkbox.isChecked(),
        UUID_REGISTRATION_TYPE: combo.itemData(combo.currentIndex()),
    }

    # ── Print the result so you can see the UUID-keyed contract ──────────
    print("\n=== Result dict (ready for deserializer) ===")
    for uuid, value in result.items():
        print(f"  {uuid!r:45s}  ->  {value!r}")
    print()

    # ── Accept the dialog — closes it and signals success ─────────────────
    # dialog.accept() sets the return code to QDialog.Accepted.
    # dialog.reject() would set it to QDialog.Rejected (used by Cancel).
    # We check this return code after exec_() in Step 9.
    dialog.accept()


def on_cancel_clicked() -> None:
    """
    Slot called when the user clicks Cancel.
    dialog.reject() closes the window with return code QDialog.Rejected.
    """
    print("[cancelled] User closed the form.")
    dialog.reject()


run_button.clicked.connect(on_run_clicked)
cancel_button.clicked.connect(on_cancel_clicked)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 9 — ENTERING THE EVENT LOOP
# ─────────────────────────────────────────────────────────────────────────────
#
# dialog.exec_() is the blocking call. It:
#   1. Shows the window.
#   2. Starts processing Qt events (mouse clicks, key presses, redraws).
#   3. BLOCKS this thread until the dialog is closed.
#   4. Returns QDialog.Accepted or QDialog.Rejected.
#
# This is identical to how the production build_form() works. The entire
# MIRACL workflow engine waits at this line until the user clicks Run or Cancel.
#
# From your C++ experience: exec() in Qt 5 is the same call you know.
# PyQt5 uses exec_() because exec is a reserved keyword in Python 2
# (the underscore convention has been kept for compatibility).

return_code = dialog.exec_()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 10 — AFTER THE EVENT LOOP
# ─────────────────────────────────────────────────────────────────────────────
#
# Once exec_() returns, we are back in normal Python code. The window is gone.
# We check the return code to decide what to do next.
#
# In the production builder, build_form() returns the result dict here
# (or None if the user cancelled). The workflow engine then calls
# deserialize_parsed_args_to_objects() with that dict.

if return_code == QtWidgets.QDialog.Accepted:
    print("Form was submitted successfully.")
    print("In the production pipeline, the result dict would now be passed")
    print("to deserialize_parsed_args_to_objects().")
else:
    print("Form was cancelled. Nothing to do.")

# sys.exit() hands the Qt event loop's exit code back to the OS.
# This is the correct way to terminate a Qt application cleanly.
sys.exit(return_code)
