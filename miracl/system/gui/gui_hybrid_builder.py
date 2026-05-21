"""
Code written and maintained by Jonas Osmann. Contact at j.osmann@alumni.utoronto.ca or
via https://github.com/AICONSlab/MIRACL/issues

PyQt5 implementation of the MIRACL GUI builder. Currently, each GUI frontend gets its
own builder. I might revisit this design choice but for now there is only one GUI
interface to deal with.

Note:
  The GUI builder receives its input from the GUI serializer who in turn receives its
  input from the registry introspector. This is nice because the introspector produces
  an agnostic output that can be serialized to any other interface, be it a GUI or the
  CLI. The GUI module does not need to know about any of the functions of the registry
  or other modules in the pipeline.

Features and design choicese:
  - Lazy loading: no actual libs loaded until script is run
  - Blocking call pattern: 'build_form' is a blocking call that never manages internal
    state or calls a separate collection method.
  - Two-pass rendering: Widget construction and dependency wiring are kept as two
    separate passes. Eliminates forward reference problems for dependencies. Currently,
    the dependency system isn't used yet but it's available in the Pydantic datamodel.
  - Widget factory: Factory method to create widgets using a dispatch.
  - Composite widgets and MIRACL_VAL_WIDGET: 'PATH_INPUT' and 'SLIDER' are composite
    widgets meaning that they are multiple Qt widgets inside a `QWidget` container.
    '_get_widget_value' and '_connect_signal` never need to know whether they received
    a simple or composite widget.
  - Label and tooltip convention: Tooltip text comes exclusively from 'spec.help_text',
    sourced from 'cli.help' by the serializer.
  - Required field validation: Performed as a sweep when the user clicks 'Run'. All
    violations are collected before any error is surfaced so the user sees the complete
    list at once. That way the user doesn't have to solve one issue at a time and run
    again to see the next error message.
  - Safe signal absorption: Qt signals emit arguments that can crash generic slots or
    unexpectedly override timer intervals. All dependency signals are safely routed
    through ''_on_dependency_changed'.
  - Debounced text signals: 'QLineEdit.textChanged' and 'QPlainTextEdit.textChanged'
    fire on every keystroke. On large forms this would call '_update_states' which loops
    the entire registry...on every character typed!! This is solved by restarting the
    timer with each keystroke so '_updated_states' is only invoked 250ms after user
    stops typing.
  - Result storage: The result dict is stored in 'self._last_result' rather than
    monkey-patched onto the dialog instance. The builder owns the state of the current
    form.

.. note::

    I still haven't fully decided on a style guide so I'm still experimenting with
    different code annotations like headers.
"""

#######################################################################################
# IMPORTS
#######################################################################################
from __future__ import annotations
import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.gui.gui_hybrid_serializer_builder_contract import (
    GuiFieldSpec,
    GuiSchema,
    GuiTab,
    GuiSerializationError,
    WidgetType,
    UNGROUPED_TAB_KEY,
)
from miracl.system.logger import get_logger

# Lazy loading
if TYPE_CHECKING:
    from PyQt5 import QtWidgets, QtCore

logger = get_logger(__name__)

#######################################################################################
# EXCEPTIONS
#######################################################################################


class ValidationError(ValueError):
    """
    Raised by MiraclPyQtGuiBuilder._collect_results when one or more required fields
    are empty at the time the user clicks Run.

    All violations are collected before this exception is raised so the user sees the
    complete list in one message rather than fixing them one at a time.

    Args:
      missing: Human-readable label strings for every empty required field
    """

    def __init__(self, missing: List[str]) -> None:
        self.missing = missing
        labels = "\n  * ".join(missing)
        super().__init__(f"The following required fields are empty:\n  * {labels}")


class CoercionError(ValueError):
    """
    Raised by MiraclPyQtGuiBuilder._coerce when a raw widget value cannot be converted
    to its target Python type.

    This error is raised here intentionally as passing an unconverted string to
    deserialize_parsed_args_to_objects would fail later with a far less informative
    traceback.

    Args:
      field_name: Human-readable name of the offending field
      raw_value: The raw value that failed conversion
      target_type: The Python type the conversion attempted to produce
      cause: The underlying TypeError or ValueError
    """

    def __init__(
        self,
        field_name: str,
        raw_value: Any,
        target_type: type,
        cause: Exception,
    ) -> None:
        self.field_name = field_name
        self.raw_value = raw_value
        self.target_type = target_type
        self.cause = cause
        # self._app: Optional["QtWidgets.QApplication"] = None
        super().__init__(
            f"Cannot convert '{raw_value}' for field '{field_name}' to {target_type.__name__}: {cause}"
        )


#######################################################################################
# WIDGET REGISTRY ENTRY
#######################################################################################


@dataclass(frozen=True)
class WidgetEntry:
    """
    Immutable pairing of a rendered Qt widget with its source specification which is
    the UUID string.

    Params:
      widget: The rendered QWidget. Can be a normal widget or a composite container.
      spec: The GuiFieldSpec from the Pydantic object that described this widget.
      Immutable! Never modified after construction!
    """

    widget: "QtWidgets.QWidget"
    spec: GuiFieldSpec


#######################################################################################
# FRONTEND-AGNOSTIC INTERFACE CONTRACT (ABC)
#######################################################################################


class MiraclGUIBuilder(abc.ABC):
    """
    Thin abstract base class defining the interface every MIRACL GUI builder
    must honour. Doesn't actually contain frontend code. It only constains
    _collect_hidden which is pure schema logic identical for every builder.

    The reason why the return type of build_form is Optional[Dict[str, Any]] rather
    than a QWidget is to keep the ABC free of any Qt import which allows future non-Qt
    builders like Gradio or web, etc.) to satisfy the same
    interface without pulling in Qt.
    """

    @abc.abstractmethod
    def build_form(self, schema: GuiSchema) -> Optional[Dict[str, Any]]:
        """
        Render a gui_parser_contracts.GuiSchema, block until the user submits or
        cancels, and return the result dict or None.

        Params:
          schema: Validated schema from the serializer
          returns: UUID-keyed dict[str, Any] on Run, None on Cancel
        """

    @staticmethod
    def _collect_hidden(schema: GuiSchema) -> Dict[str, Any]:
        """
        Seed the result dict with placeholder values for all INTERNAL (hidden) args.

        The workflow engine overwrites these at runtime, but the UUID keys must be
        present for the deserializer to operate in strict mode. Lives on the ABC
        because it has no frontend dependency. It is pure schema logic identical
        for every builder.

        Params:
          schema: The schema being rendered
          returns: {arg.dest: arg.default} for every hidden argument
        """
        return {arg.dest: arg.default for arg in schema.hidden}


#######################################################################################
# CONCRETE BUILDER  —  PyQt5 implementation
#######################################################################################


class MiraclPyQtGuiBuilder(MiraclGUIBuilder):
    """
    PyQt5 implementation of the MIRACL GUI builder. Pretty important!

    Renders a gui_parser_contracts.GuiSchema into a QDialog, manages widget state via
    dependency logic, validates required fields, coerces widget values to their target
    Python types, and returns a UUID-keyed result dict.

    Note:
      In terms of lifecycle, a single instance may be reused across multiple
      build_form calls. Internal state (registry, result, timer) is fully reset at the
      start of each call.

    Params:
      _schema: The schema currently being rendered
      _registry: UUID dest -> WidgetEntry
      _last_result: Result dict from the most recent accepted form
      _debounce_timer: QTimer that throttles text-widget signal callbacks to avoid
                       calling _update_states on every keystroke.
    """

    def __init__(self) -> None:
        self._schema: Optional[GuiSchema] = None
        self._registry: Dict[str, WidgetEntry] = {}
        self._last_result: Optional[Dict[str, Any]] = None
        self._debounce_timer: Optional["QtCore.QTimer"] = None

        self._tab_widget: Optional["QtWidgets.QTabWidget"] = None
        self._optional_tab_indices: List[int] = []
        self._has_required_tab: bool = False

        # Qt module references. These are populated by the lazy import in build_form().
        self._QtWidgets: Any = None
        self._QtCore: Any = None
        self._QtGui: Any = None

        # NOTE: Moved out of build_form since the dict didn't need to be reconstructed
        # every time each time a widget is created.
        self._widget_dispatch: Dict[
            WidgetType, Callable[[GuiFieldSpec], "QtWidgets.QWidget"]
        ] = {
            WidgetType.SPINBOX: self._make_spinbox,
            WidgetType.DOUBLE_SPINBOX: self._make_double_spinbox,
            WidgetType.NULLABLE_DOUBLE_SPINBOX: self._make_nullable_double_spinbox,
            WidgetType.LINE_EDIT: self._make_line_edit,
            WidgetType.CHECKBOX: self._make_checkbox,
            WidgetType.COMBO_BOX: self._make_combo,
            WidgetType.PATH_INPUT: self._make_path_input,
            WidgetType.SLIDER: self._make_slider,
            WidgetType.TEXT_AREA: self._make_text_area,
            WidgetType.MULTI_LINE_EDIT: self._make_multi_line_edit,
        }

        logger.info("Initialized PyQt GUI builder")

    ###################################################################################
    # PUBLIC API
    ###################################################################################

    def build_form(self, schema: GuiSchema) -> Optional[Dict[str, Any]]:
        """
        Render the schema into a blocking QDialog and return the result.

        PyQt5 is imported here instead of at module level. Importing this module costs
        nothing on the CLI path where Qt is never needed.

        Performs four phases:
          1. Reset: Clear all state from any previous call
          2. Render: Build the dialog, header, tab widget, and all field widgets. Every
                     widget is registered in _registry by UUID.
          3. Wire: Connect value-changed signals to the dependency update slot via the
                   debounce timer. Run an initial state update so widgets that depend
                   on empty fields start disabled.
          4. Block: Call dialog.exec() to enter the Qt event loop. Returns when the
                    user clicks Run (accepted) or Cancel. Cancel closes the window.

        If the user clicks Run, _on_run_clicked calls _collect_results. On success the
        result dict is stored in self._last_result and the dialog accepts. On
        validation or coercion failure the dialog stays open and a QMessageBox
        describes the problem.

        Params:
          schema: Validated gui_parser_contracts.GuiSchema
          returns: UUID-keyed dict[str, Any] on Run, None on Cancel
        """
        # Lazy import. Qt only loaded when GUI is actually requested
        from PyQt5 import QtWidgets, QtCore, QtGui

        self._QtWidgets = QtWidgets
        self._QtCore = QtCore
        self._QtGui = QtGui

        # Phase 1: reset
        self._schema = schema
        self._registry = {}
        self._last_result = None

        # Debounce timer. Single-shot, 250ms. Text widgets connect to timer.start()
        # instead of _update_states directly. Every keystroke restarts the 250ms
        # countdown. _update_states only fires once the user stops typing for 250ms.
        self._debounce_timer = QtCore.QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(250)
        self._debounce_timer.timeout.connect(self._update_states)

        logger.info(
            "Building PyQt form | command=%s | tabs=%d",
            schema.meta.command,
            len(schema.tabs),
        )

        # QApplication must exist before any QWidget is created. Reuse an existing
        # instance if one already exists (e.g. in tests).
        self._app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

        # Phase 2: render
        dialog = QtWidgets.QDialog()
        dialog.setAttribute(
            QtCore.Qt.WA_DeleteOnClose
        )  # Immediate C++ memory cleanup. I wish I was actually writing this in C++...
        dialog.setWindowTitle(schema.meta.title or f"MIRACL - {schema.meta.command}")
        dialog.setMinimumWidth(700)
        dialog.resize(850, 550)
        dialog.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        root_layout = QtWidgets.QVBoxLayout(dialog)
        root_layout.setSpacing(8)
        root_layout.setContentsMargins(12, 12, 12, 12)

        root_layout.addWidget(self._build_header(schema))
        root_layout.addWidget(self._build_tabs(schema))

        # Only show required tabs at GUI startup. Show optional tabs checkbox.
        if self._has_required_tab and self._optional_tab_indices:
            show_cb = self._QtWidgets.QCheckBox("Show optional arguments")
            # NOTE: Initial state of the optional tabs visibility.
            # False: Checkbox not checked -> optional tabs hidden when GUI starts
            # True: Checkbox checked -> optional tabs shown when GUI starts
            show_cb.setChecked(False)
            show_cb.stateChanged.connect(self._on_show_optional_tabs)
            self._on_show_optional_tabs(
                show_cb.checkState()
            )  # Immediatly communicate checkbox state to show optional tabs method
            root_layout.addWidget(show_cb)

        root_layout.addWidget(self._build_footer(dialog))

        # Phase 3: wire
        self._wire_dependencies()

        # Phase 4: block
        # exec() enters the Qt event loop and blocks until the dialog closes.
        # _last_result is populated by _on_run_clicked on successful submission.
        accepted = dialog.exec() == QtWidgets.QDialog.Accepted

        if not accepted:
            logger.info("User cancelled | command=%s", schema.meta.command)
            return None

        logger.info("Form accepted | command=%s", schema.meta.command)
        return self._last_result

    ###################################################################################
    # RENDER PHASE HELPERS
    ###################################################################################

    def _build_header(self, schema: GuiSchema) -> "QtWidgets.QWidget":
        """
        Build the top bar: title label, status badges, and optional help button.

        Params:
          schema: The schema whose meta block drives the header
          returns: A QWidget for insertion at the top of the root layout
        """
        QtWidgets = self._QtWidgets
        QtCore = self._QtCore

        header = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # title = QtWidgets.QLabel(
        #     f"<b>{schema.meta.title}</b>"
        #     or f"<b>{schema.meta.module}</b> - {schema.meta.command}"
        # )
        # FIX: This is not actually working. Figure out why when you've got time.
        if schema.meta.title is None:
            logger.info(
                "meta.title is missing in registry YAML | module=%s | command=%s",
                schema.meta.module,
                schema.meta.command,
            )
        title_text = (
            f"<b>{schema.meta.title}</b>"
            if schema.meta.title
            else f"<b>{schema.meta.module}</b> - {schema.meta.command}"
        )
        title = QtWidgets.QLabel(title_text)
        title.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(title)

        # WARNING: This conditional logic prevents both banners from being shown. If both
        # are true, only deprecated will be displayed, overriding experimental.
        # I should reconsider this at a later date.
        if schema.meta.deprecated:
            msg = schema.meta.deprecation_message or "This command is deprecated."
            banner = QtWidgets.QLabel(f"{msg}")
            layout.addWidget(banner)
        elif schema.meta.experimental:
            banner = QtWidgets.QLabel("Experimental")
            layout.addWidget(banner)

        layout.addStretch()

        if schema.meta.help:
            help_btn = QtWidgets.QPushButton("?")
            help_btn.setFixedSize(26, 26)
            help_btn.setToolTip("Help for this module/workflow")
            help_btn.clicked.connect(lambda: self._show_help_dialog(schema))
            layout.addWidget(help_btn)

        return header

    def _show_help_dialog(self, schema: GuiSchema) -> None:
        """
        Open a modal ``QMessageBox`` showing full help content from ``schema.meta``.

        Params:
          schema: The schema whose meta block supplies the content as defined in the
                  YAML config file.
        """
        QtWidgets = self._QtWidgets
        meta = schema.meta
        lines: List[str] = []

        if meta.help:
            lines.append(meta.help)
        if meta.extended_help:
            lines.extend(["", meta.extended_help])
        if meta.docs_url:
            lines.extend(["", f"Documentation: {meta.docs_url}"])

        hints: List[str] = []
        if meta.version:
            hints.append(f"Version: {meta.version}")
        if meta.requires_gpu:
            hints.append("Requires GPU")
        if meta.min_memory_gb:
            hints.append(f"Min RAM: {meta.min_memory_gb}")
        if meta.estimated_runtime:
            hints.append(f"Estimated runtime: {meta.estimated_runtime}")
        if hints:
            lines.extend(["", " | ".join(hints)])

        QtWidgets.QMessageBox.information(
            None,
            f"About {meta.command}",
            "\n".join(lines),
        )

    def _build_tabs(self, schema: GuiSchema) -> "QtWidgets.QTabWidget":
        """
        Build the QTabWidget. Tabs are based on module groups and mirror the arpgarser
        groups from the CLI. One tab per entry in schema.tabs.

        The sentinel gui_parser_contracts.UNGROUPED_TAB_KEY is displayed as "General"
        so implementation details never surface in the UI. Tab descriptions from
        GuiTabMeta are set as tooltips. Technically this should never be triggered as
        each module group should be defined in their respective Pydantic objects and
        enums.

        Params:
          schema: The schema whose tabs dict drives tab creation
          returns: A populated QTabWidget
        """
        QtWidgets = self._QtWidgets

        tab_widget = QtWidgets.QTabWidget()

        # Reset tracking state in case build_form is called multiple times on same
        # builder instance
        self._optional_tab_indices = []
        self._has_required_tab = False

        for tab_key, tab_data in schema.tabs.items():
            scroll_area = self._build_tab(tab_data)
            display_label = (
                "General" if tab_key == UNGROUPED_TAB_KEY else tab_data.tab_meta.label
            )

            # Capture int idx of this tab in QTabWidget
            index = tab_widget.addTab(scroll_area, display_label)

            if tab_data.tab_meta.description:
                tab_widget.setTabToolTip(index, tab_data.tab_meta.description)

            # Is tab required or optional?
            # if tab_key == CliGroup.REQUIRED.ref:
            if any(spec.required for spec in tab_data.args):
                self._has_required_tab = True
            else:
                self._optional_tab_indices.append(index)

        # If a required tab exists, hide optional tabs at startup
        # if self._has_required_tab:
        #     for idx in self._optional_tab_indices:
        #         tab_widget.setTabVisible(idx, False)

        # Store widget ref for checkbox callback
        self._tab_widget = tab_widget

        return tab_widget

    def _on_show_optional_tabs(self, state: int) -> None:
        if self._tab_widget is None:
            return
        visible = bool(state)
        for idx in self._optional_tab_indices:
            self._tab_widget.setTabVisible(idx, visible)

    def _build_tab(self, tab_data: GuiTab) -> "QtWidgets.QScrollArea":
        """
        Build a single scrollable tab panel from a gui_parser_contracts.GuiTab.

        Each gui_parser_contracts.GuiFieldSpec is rendered via _create_widget,
        registered in _registry, and added to a QFormLayout row.

        Label text: spec.label joined with " / " except for MULTI_LINE_EDIT which
        always chooses idx 0 as the main label and the indices at the remaining labels
        as sub labels. Required fields get a trailing " *", although I might change
        that at some point. Deprecated fields are marked with " (deprecated)". For
        tooltips, spec.help_text is the primary source and additional_labels are
        appended when present.

        Params:
          tab_data: The gui_parser_contracts.GuiTab to render
          returns: A QScrollArea wrapping the form layout
        """
        QtWidgets = self._QtWidgets
        QtCore = self._QtCore

        inner = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(inner)
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        form.setVerticalSpacing(6)
        form.setHorizontalSpacing(12)

        for spec in tab_data.args:
            widget = self._create_widget(spec)
            self._registry[spec.dest] = WidgetEntry(widget=widget, spec=spec)

            if spec.widget_type == WidgetType.MULTI_LINE_EDIT:
                label_text = spec.label[0]
            else:
                label_text = " / ".join(spec.label)

            if spec.required:
                label_text += f" *"
            if spec.deprecated:
                label_text += f" (deprecated)"
            label_text += " :"

            label_widget = QtWidgets.QLabel(label_text)

            tooltip_parts: List[str] = []
            if spec.help_text:
                tooltip_parts.append(spec.help_text)
            if spec.additional_labels:
                tooltip_parts.extend(spec.additional_labels)
            if tooltip_parts:
                tooltip = "\n".join(tooltip_parts)
                label_widget.setToolTip(tooltip)
                widget.setToolTip(tooltip)

            form.addRow(label_widget, widget)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner)
        return scroll

    def _build_footer(self, dialog: "QtWidgets.QDialog") -> "QtWidgets.QWidget":
        """
        Build the footer bar containing Run and Cancel buttons.

        Params:
          dialog: The parent QDialog
          returns: A QWidget containing the button row
        """
        QtWidgets = self._QtWidgets

        footer = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(footer)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.addStretch()

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        run_btn = QtWidgets.QPushButton("Run")
        run_btn.setDefault(True)
        run_btn.clicked.connect(lambda: self._on_run_clicked(dialog))
        layout.addWidget(run_btn)

        return footer

    ###################################################################################
    # RUN ACTION
    ###################################################################################

    def _on_run_clicked(self, dialog: "QtWidgets.QDialog") -> None:
        """
        Handle a click on the Run button.

        Calls _collect_results. On success stores the result in _last_result and calls
        dialog.accept(). On failure shows a QMessageBox and leaves the dialog open.

        Params:
          dialog: The parent QDialog.
        """
        QtWidgets = self._QtWidgets

        try:
            results = self._collect_results()
        except ValidationError as exc:
            QtWidgets.QMessageBox.warning(
                dialog,
                "Required fields missing",
                str(exc),
            )
            return
        except CoercionError as exc:
            QtWidgets.QMessageBox.critical(
                dialog,
                "Type conversion error",
                str(exc),
            )
            return

        # Store on self rather than monkey-patching the dialog.
        self._last_result = results
        dialog.accept()

    def _collect_results(self) -> Dict[str, Any]:
        """
        Sweep all registered widgets, validate required fields, coerce values, and
        return the complete UUID-keyed result dict. Super important method!!

        Steps:
          1. Seed with hidden-arg defaults via _collect_hidden
          2. Extract raw values from every widget via _get_widget_value
          3. Sweep for required violations and collect all before raising
          4. Coerce each value to its target type via _coerce

        Params:
          returns: UUID-keyed dict[str, Any] of coerced Python values
          ValidationError: If any required field is empty
          CoercionError: If any value cannot be coerced to its type
        """
        assert self._schema is not None, (
            "_collect_results() called before build_form() - internal error"
        )

        if self._debounce_timer is not None and self._debounce_timer.isActive():
            self._debounce_timer.stop()
            self._update_states()

        results: Dict[str, Any] = self._collect_hidden(self._schema)

        # Step 1: extract all raw values first
        raw: Dict[str, Any] = {
            dest: self._get_widget_value(entry.widget, entry.spec)
            for dest, entry in self._registry.items()
        }

        # Step 2: collect all required violations before raising
        missing: List[str] = [
            " / ".join(entry.spec.label)
            for dest, entry in self._registry.items()
            if entry.spec.required
            and entry.widget.isEnabled()  # Prevent blocking on disabled fields
            and self._is_empty(raw[dest])
        ]
        if missing:
            raise ValidationError(missing)

        # Step 3: coercion
        for dest, entry in self._registry.items():
            results[dest] = self._coerce(raw[dest], entry.spec)

        return results

    ###################################################################################
    # WIDGET FACTORY
    ###################################################################################

    def _create_widget(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Dispatch to the appropriate _make_* method based on
        gui_parser_contracts.GuiFieldSpec.widget_type.

        Uses a dispatch dict rather than a chain of conditionals so adding a new widget
        type requires only one new dict entry and one new _make_* method.

        Raises immediately for unimplemented types rather than rendering a silent
        placeholder.

        Params:
          spec: The field specification to render
          returns: A rendered QWidget
          GuiSerializationError: For any unimplemented WidgetType
        """
        # dispatch: Dict[WidgetType, Callable[[GuiFieldSpec], "QtWidgets.QWidget"]] = {
        #     WidgetType.SPINBOX: self._make_spinbox,
        #     WidgetType.DOUBLE_SPINBOX: self._make_double_spinbox,
        #     WidgetType.NULLABLE_DOUBLE_SPINBOX: self._make_nullable_double_spinbox,
        #     WidgetType.LINE_EDIT: self._make_line_edit,
        #     WidgetType.CHECKBOX: self._make_checkbox,
        #     WidgetType.COMBO_BOX: self._make_combo,
        #     WidgetType.PATH_INPUT: self._make_path_input,
        #     WidgetType.SLIDER: self._make_slider,
        #     WidgetType.TEXT_AREA: self._make_text_area,
        #     WidgetType.MULTI_LINE_EDIT: self._make_multi_line_edit,
        # }

        # factory = dispatch.get(spec.widget_type)
        factory = self._widget_dispatch.get(spec.widget_type)
        if factory is None:
            raise GuiSerializationError(
                f"'{spec.name}' has widget_type='{spec.widget_type.value}' which is not yet implemented in MiraclPyQtGuiBuilder. Add a '_make_{spec.widget_type.value.lower()}' method."
            )

        logger.debug(
            "Creating widget | dest=%s | type=%s",
            spec.dest,
            spec.widget_type.value,
        )
        return factory(spec)

    ###################################################################################
    # WIDGET MAKERS
    ###################################################################################

    def _make_spinbox(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a QSpinBox for integer arguments.

        The contract guarantees that any field routed here has widget_type=SPINBOX and
        value_type=int. No runtime type detection is needed or performed.

        Range props are applied from spec.props.range when present. The contract also
        guarantees that max_val is always explicitly declared for SPINBOX fields in
        the Pydantic object definitions so Qt's default maximum of 99 is always
        overridden.

        An optional Qt-specific "suffix" extension string is applied when present in
        spec.extensions["qt"].

        Params:
          spec: Field specification. Contract guarantees SPINBOX + int.
          returns: A configured QSpinBox
        """
        QtWidgets = self._QtWidgets
        widget = QtWidgets.QSpinBox()

        if spec.props.range:
            rng = spec.props.range
            if rng.min_val is not None:
                widget.setMinimum(int(rng.min_val))
            if rng.max_val is not None:
                widget.setMaximum(int(rng.max_val))
            if rng.increment_val is not None:
                widget.setSingleStep(int(rng.increment_val))

        qt_ext = spec.extensions.get("qt", {})
        if "suffix" in qt_ext:
            widget.setSuffix(f" {qt_ext['suffix']}")

        if spec.default is not None:
            try:
                widget.setValue(int(spec.default))
            except (TypeError, ValueError):
                logger.warning(
                    "Could not set spinbox default | dest=%s | default=%s",
                    spec.dest,
                    spec.default,
                )

        return widget

    def _make_double_spinbox(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a QDoubleSpinBox for float arguments.

        The contract guarantees that any field routed here has
        widget_type=DOUBLE_SPINBOX and value_type=float. No runtime type detection is
        needed or performed.

        Range props are applied from spec.props.range when present. The contract also
        guarantees that max_val is always explicitly declared for DOUBLE_SPINBOX
        fields, so Qt's default maximum of 99.99 is always overridden.

        nr_decimals controls the number of decimal places displayed and accepted. An
        optional Qt-specific "suffix" extension string is applied when present in
        spec.extensions["qt"].

        Params:
          spec: Field specification. Contract guarantees DOUBLE_SPINBOX + float.
          returns: A configured QDoubleSpinBox
        """
        QtWidgets = self._QtWidgets
        widget = QtWidgets.QDoubleSpinBox()

        if spec.props.range:
            rng = spec.props.range
            if rng.min_val is not None:
                widget.setMinimum(rng.min_val)
            if rng.max_val is not None:
                widget.setMaximum(rng.max_val)
            if rng.increment_val is not None:
                widget.setSingleStep(rng.increment_val)
            if rng.nr_decimals is not None:
                widget.setDecimals(rng.nr_decimals)

        qt_ext = spec.extensions.get("qt", {})
        if "suffix" in qt_ext:
            widget.setSuffix(f" {qt_ext['suffix']}")

        if spec.default is not None:
            try:
                widget.setValue(float(spec.default))
            except (TypeError, ValueError):
                logger.warning(
                    "Could not set double spinbox default | dest=%s | default=%s",
                    spec.dest,
                    spec.default,
                )

        return widget

    def _make_nullable_double_spinbox(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a composite nullable float input: QCheckBox + QDoubleSpinBox.

        When the checkbox is unchecked (default), the spinbox is disabled and the
        widget returns None. When checked, the spinbox is enabled and returns the float
        value. This is used for optional float arguments that have a meaningful None
        state distinct from any numeric value. The reason I had to come up with this
        widget are the questionable design decisions of some of the ppl writing
        methods that are being integrated as modules into MIRACL :P

        The MIRACL_VAL_WIDGET property on the container points to the checkbox, which
        acts as the gate. Value extraction handles both states.

        Params:
          spec: Field specification. Contract guarantees NULLABLE_DOUBLE_SPINBOX + float.
          returns: A composite QWidget container
        """
        QtWidgets = self._QtWidgets

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        checkbox = QtWidgets.QCheckBox()
        spinbox = QtWidgets.QDoubleSpinBox()
        spinbox.setEnabled(False)  # Disabled until checkbox is ticked

        if spec.props.range:
            rng = spec.props.range
            if rng.min_val is not None:
                spinbox.setMinimum(rng.min_val)
            if rng.max_val is not None:
                spinbox.setMaximum(rng.max_val)
            if rng.increment_val is not None:
                spinbox.setSingleStep(rng.increment_val)
            if rng.nr_decimals is not None:
                spinbox.setDecimals(rng.nr_decimals)

        if spec.default is not None:
            try:
                spinbox.setValue(float(spec.default))
            except (TypeError, ValueError):
                pass

        checkbox.stateChanged.connect(lambda state: spinbox.setEnabled(bool(state)))

        layout.addWidget(checkbox)
        layout.addWidget(spinbox)

        # Store both widgets as properties for value extraction
        container.setProperty("MIRACL_VAL_WIDGET", checkbox)
        container.setProperty("MIRACL_SPINBOX_WIDGET", spinbox)

        return container

    def _make_line_edit(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a QLineEdit for free-text or restricted string input.

        Input restriction validators are applied from
        spec.props.text.input_restrictions when present.

        Params:
          spec: Field specification
          returns: A configured QLineEdit
        """
        QtWidgets = self._QtWidgets
        QtGui = self._QtGui

        widget = QtWidgets.QLineEdit()

        if spec.default is not None:
            if isinstance(spec.default, list):
                widget.setText(" ".join(str(v) for v in spec.default))
            else:
                widget.setText(str(spec.default))

        if spec.props.text and spec.props.text.input_restrictions:
            restriction = spec.props.text.input_restrictions
            if restriction == "INTEGERS_ONLY":
                widget.setValidator(QtGui.QIntValidator())
            elif restriction == "FLOATS_ONLY":
                widget.setValidator(
                    QtGui.QRegularExpressionValidator(
                        self._QtCore.QRegularExpression(r"^-?\d*\.?\d*$")
                    )
                )

        qt_ext = spec.extensions.get("qt", {})
        if "placeholder" in qt_ext:
            widget.setPlaceholderText(qt_ext["placeholder"])

        return widget

    def _make_checkbox(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a QCheckBox for boolean arguments.

        The string "true" (case-insensitive) is treated as True when the default
        arrives as a string from the serializer.

        Params:
          spec: Field specification
          returns: A configured QCheckBox
        """
        QtWidgets = self._QtWidgets

        widget = QtWidgets.QCheckBox()
        default = spec.default
        if isinstance(default, str):
            default = default.strip().lower() == "true"
        widget.setChecked(bool(default))
        return widget

    def _make_combo(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a QComboBox for choice arguments.

        Each choice value is stored as item data via addItem(label, data).  Display
        labels come from spec.props.choices.vals when present.

        The default is matched by comparing str(item_data) against str(spec.default)
        to normalise int/str type mismatches.

        Params:
          spec: Field specification.
          returns: A configured ``QComboBox``.
        """
        QtWidgets = self._QtWidgets

        widget = QtWidgets.QComboBox()
        choices = spec.choices or []
        gui_labels = (
            spec.props.choices.vals
            if spec.props.choices and spec.props.choices.vals
            else None
        )

        for index, value in enumerate(choices):
            display = (
                gui_labels[index]
                if gui_labels and index < len(gui_labels)
                else str(value)
            )
            widget.addItem(display, value)

        if spec.default is not None:
            for index in range(widget.count()):
                if str(widget.itemData(index)) == str(spec.default):
                    widget.setCurrentIndex(index)
                    break

        return widget

    # NOTE: We also need a chooser for files, not only for directories

    def _make_path_input(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a composite path input: QLineEdit + Browse… button.

        The MIRACL_VAL_WIDGET property on the container points to the inner QLineEdit
        so value extraction and signal connection work transparently on the container.
        Qt extension key "path_type": "file" -> getOpenFileName; "directory" (default)
        -> getExistingDirectory.

        Params:
          spec: Field specification.
          returns: A composite ``QWidget`` container.
        """
        QtWidgets = self._QtWidgets

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        line_edit = QtWidgets.QLineEdit()
        if spec.default is not None:
            line_edit.setText(str(spec.default))

        qt_ext = spec.extensions.get("qt", {})
        path_type = qt_ext.get("path_type", "directory")

        def browse() -> None:
            if path_type == "file":
                path, _ = QtWidgets.QFileDialog.getOpenFileName(
                    container, "Select File"
                )
            else:
                path = QtWidgets.QFileDialog.getExistingDirectory(
                    container, "Select Directory"
                )
            if path:
                line_edit.setText(path)

        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(browse)

        layout.addWidget(line_edit)
        layout.addWidget(browse_btn)

        container.setProperty("MIRACL_VAL_WIDGET", line_edit)
        return container

    def _make_slider(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a composite slider: QSlider + live value QLabel.

        The label updates on every valueChanged signal. The MIRACL_VAL_WIDGET property
        on the container points to the inner QSlider.

        Params:
          spec: Field specification.
          returns: A composite ``QWidget`` container.
        """
        QtWidgets = self._QtWidgets
        QtCore = self._QtCore

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        value_label = QtWidgets.QLabel("0")
        value_label.setFixedWidth(40)

        if spec.props.range:
            rng = spec.props.range
            if rng.min_val is not None:
                slider.setMinimum(int(rng.min_val))
            if rng.max_val is not None:
                slider.setMaximum(int(rng.max_val))
            if rng.increment_val is not None:
                slider.setSingleStep(int(rng.increment_val))

        if spec.default is not None:
            try:
                slider.setValue(int(spec.default))
            except (TypeError, ValueError):
                pass

        slider.valueChanged.connect(value_label.setNum)
        value_label.setNum(slider.value())

        layout.addWidget(slider)
        layout.addWidget(value_label)

        container.setProperty("MIRACL_VAL_WIDGET", slider)
        return container

    def _make_text_area(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        """
        Create a QPlainTextEdit for multi-line text input.

        Respects an optional "height" key in spec.extensions["qt"] to fix the widget
        height in pixels.

        Params:
          spec: Field specification.
          returns: A configured ``QPlainTextEdit``.
        """
        QtWidgets = self._QtWidgets

        widget = QtWidgets.QPlainTextEdit()
        if spec.default is not None:
            widget.setPlainText(str(spec.default))

        qt_ext = spec.extensions.get("qt", {})
        if "height" in qt_ext:
            widget.setFixedHeight(int(qt_ext["height"]))

        return widget

    def _make_multi_line_edit(self, spec: GuiFieldSpec) -> "QtWidgets.QWidget":
        QtWidgets = self._QtWidgets

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        n = (
            len(spec.default)
            if isinstance(spec.default, list)
            else max(
                len(spec.label) - 1, 1
            )  # label[0] is the main widget label and label [1:] are the sub-field labels
        )
        sub_labels = spec.label[1:] if len(spec.label) > 1 else []
        line_edits = []

        for i in range(n):
            sub = QtWidgets.QWidget()
            sub_layout = QtWidgets.QHBoxLayout(sub)
            sub_layout.setContentsMargins(0, 0, 0, 0)
            sub_layout.setSpacing(1)

            lbl = QtWidgets.QLabel(sub_labels[i] if i < len(sub_labels) else str(i + 1))
            # lbl.setStyleSheet("font-size: 9px; color: gray;")
            sub_layout.addWidget(lbl)

            le = QtWidgets.QLineEdit()
            if isinstance(spec.default, list) and i < len(spec.default):
                le.setText(str(spec.default[i]))
            sub_layout.addWidget(le)
            line_edits.append(le)

            layout.addWidget(sub)

        container.setProperty("MIRACL_VAL_WIDGET", line_edits)
        return container

    ###################################################################################
    # WIRE PHASE
    ###################################################################################

    def _wire_dependencies(self) -> None:
        """
        Pass 2: connect value-changed signals to the debounce timer, which in turn
        calls _update_states after a 250ms pause. Each unique dependency target UUID is
        wired exactly once. Connecting the same signal multiple times would fire
        redundant updates.

        After wiring, _update_states is called once immediately so widgets that depend
        on currently-empty fields start disabled.
        """
        dep_sources = {
            uuid
            for entry in self._registry.values()
            for uuid in (entry.spec.depends_on or [])
            + (entry.spec.conflicts_with or [])
            if uuid in self._registry
        }
        for uuid in dep_sources:
            target_entry = self._registry[uuid]
            self._connect_signal(
                target_entry.widget, target_entry.spec, self._on_dependency_changed
            )
        self._update_states()

        # wired: set = set()
        #
        # for entry in self._registry.values():
        #     all_deps = set(entry.spec.depends_on or []) | set(
        #         entry.spec.conflicts_with or []
        #     )
        #     for target_uuid in all_deps:
        #         if target_uuid in self._registry and target_uuid not in wired:
        #             target_entry = self._registry[target_uuid]
        #             self._connect_signal(
        #                 target_entry.widget,
        #                 target_entry.spec,
        #                 self._on_dependency_changed,
        #             )
        #             wired.add(target_uuid)
        #             logger.debug("Wired dependency | target=%s", target_uuid)
        #
        # # Initial state sweep before any user interaction
        # self._update_states()

    def _on_dependency_changed(self, *args: Any) -> None:
        """
        Absorb arbitrary signal arguments (like strings or ints emitted by
        textChanged/valueChanged) and safely restart the debounce timer.
        """
        if self._debounce_timer is not None:
            self._debounce_timer.start()

    def _update_states(self) -> None:
        """
        Evaluate depends_on and conflicts_with for every registered widget and call
        setEnabled accordingly.

        Called once at the end of _wire_dependencies and again whenever the debounce
        timer fires (i.e. 250ms after the last keystroke in any dependency widget).

        Rules:
          depends_on: disabled if any listed UUID's widget is empty
          conflicts_with: disabled if any listed UUID's widget is non-empty

        Both rules are evaluated independently and combined with logical AND.
        """
        for entry in self._registry.values():
            spec = entry.spec
            enabled = True

            if spec.depends_on:
                for dep_uuid in spec.depends_on:
                    if self._is_empty(self._get_val_by_uuid(dep_uuid)):
                        enabled = False
                        break

            if enabled and spec.conflicts_with:
                for conf_uuid in spec.conflicts_with:
                    if not self._is_empty(self._get_val_by_uuid(conf_uuid)):
                        enabled = False
                        break

            entry.widget.setEnabled(enabled)

    ###################################################################################
    # VALUE EXTRACTION HELPERS
    ###################################################################################

    # BUG: This should raise!!! Not silently return None!!!
    def _get_val_by_uuid(self, uuid_str: str) -> Any:
        """
        Extract the current value of the widget registered under uuid_str. Returns None
        if uuid_str is not in _registry.

        Params:
          uuid_str: UUID dest string
          returns: Current widget value, or None if not found
        """
        entry = self._registry.get(uuid_str)
        if entry is None:
            logger.error("UUID not found in registry | uuid=%s", uuid_str)
            raise KeyError(
                f"Widget UUID '{uuid_str}' not found in registry. Check dependency wiring and field declarations."
            )
        return self._get_widget_value(entry.widget, entry.spec)

    def _get_widget_value(self, widget: "QtWidgets.QWidget", spec: GuiFieldSpec) -> Any:
        """
        Extract the current value from a widget, resolving composite widgets via the
        MIRACL_VAL_WIDGET dynamic property transparently.

        Params:
          widget: The outer widget from _registry
          spec: The corresponding field specification
          returns: The current user-supplied value, or None
        """
        inner = widget.property("MIRACL_VAL_WIDGET") or widget

        if spec.widget_type in (
            WidgetType.SPINBOX,
            WidgetType.DOUBLE_SPINBOX,
            WidgetType.SLIDER,
        ):
            # NOTE: return inner.value() <- this is not save since float emits in IEEE754
            # double. The new confitional here round for SPINBOX and SLIDER.
            if (
                spec.widget_type == WidgetType.SPINBOX
                or spec.widget_type == WidgetType.SLIDER
            ):
                return inner.value()
            elif spec.widget_type == WidgetType.DOUBLE_SPINBOX:
                return round(inner.value(), inner.decimals())
        elif spec.widget_type == WidgetType.NULLABLE_DOUBLE_SPINBOX:
            checkbox = widget.property("MIRACL_VAL_WIDGET")
            spinbox = widget.property("MIRACL_SPINBOX_WIDGET")
            # NOTE: return inner.value() <- this is not save since float emits in IEEE754
            # double. The new confitional here round for NULLABLE_DOUBLE_SPINBOX.
            return (
                round(spinbox.value(), spinbox.decimals())
                if checkbox.isChecked()
                else None
            )
        elif spec.widget_type in (WidgetType.LINE_EDIT, WidgetType.PATH_INPUT):
            text = inner.text()
            # FIX: Ugly workaround to convert commas to '.'. For some reason I haven't been
            # able to figure this out yet, my regex is not working for floats in the line
            # input. See this conditional for context: 'elif restriction == "FLOATS_ONLY":'
            if spec.get_value_type() is float:
                text = text.replace(",", ".")
            return text
        elif spec.widget_type == WidgetType.CHECKBOX:
            return inner.isChecked()
        elif spec.widget_type == WidgetType.COMBO_BOX:
            return inner.itemData(inner.currentIndex())
        elif spec.widget_type == WidgetType.TEXT_AREA:
            return inner.toPlainText()
        elif spec.widget_type == WidgetType.MULTI_LINE_EDIT:
            return [le.text() for le in inner]

        logger.warning(
            "Unrecognised widget type in _get_widget_value | dest=%s | type=%s",
            spec.dest,
            spec.widget_type.value,
        )
        return None

    def _connect_signal(
        self, widget: "QtWidgets.QWidget", spec: GuiFieldSpec, slot: Callable
    ) -> None:
        """
        Connect a widget's primary value-changed signal to slot. Resolves composite
        widgets via MIRACL_VAL_WIDGET first.

        Params:
          widget: The outer widget whose signal to connect.
          spec: The corresponding field specification.
          slot: The callable to invoke on value change.
        """
        inner = widget.property("MIRACL_VAL_WIDGET") or widget

        if spec.widget_type in (
            WidgetType.SPINBOX,
            WidgetType.DOUBLE_SPINBOX,
            WidgetType.SLIDER,
        ):
            inner.valueChanged.connect(slot)
        elif spec.widget_type == WidgetType.NULLABLE_DOUBLE_SPINBOX:
            inner.stateChanged.connect(
                slot
            )  # inner is not the spinbox but the checkbox via MIRACL_VAL_WIDGET
        elif spec.widget_type in (WidgetType.LINE_EDIT, WidgetType.PATH_INPUT):
            inner.textChanged.connect(slot)  # emits str
        elif spec.widget_type == WidgetType.TEXT_AREA:
            inner.textChanged.connect(slot)  # emits nothing — slot must use *args
        elif spec.widget_type == WidgetType.CHECKBOX:
            inner.stateChanged.connect(slot)
        elif spec.widget_type == WidgetType.COMBO_BOX:
            inner.currentIndexChanged.connect(slot)
        elif spec.widget_type == WidgetType.MULTI_LINE_EDIT:
            for le in inner:
                le.textChanged.connect(slot)

    ###################################################################################
    # COERCION AND VALIDATION HELPERS
    ###################################################################################

    def _coerce(self, raw_value: Any, spec: GuiFieldSpec) -> Any:
        """
        Convert a raw widget value to its target Python type.

        Returns raw_value unchanged if spec.value_type is None or raw_value is None.

        Params:
          raw_value: The value from :meth:`_get_widget_value`.
          spec: The field specification.
          returns: The coerced value.
          CoercionError: If conversion fails.
        """
        if spec.required and isinstance(raw_value, str) and not raw_value.strip():
            raise RuntimeError(
                f"_coerce received empty string for required field '{' / '.join(spec.label)}' - validation sweep must run before coercion. Internal error."
            )
        if isinstance(raw_value, str) and not raw_value.strip():
            return None
        if raw_value is None:
            return None

        target_type = spec.get_value_type()
        if target_type is None:
            return raw_value

        if target_type is list:
            return raw_value.split() if isinstance(raw_value, str) else raw_value

        try:
            return target_type(raw_value)
        except (TypeError, ValueError) as exc:
            raise CoercionError(
                field_name=" / ".join(spec.label),
                raw_value=raw_value,
                target_type=target_type,
                cause=exc,
            ) from exc

    @staticmethod
    def _is_empty(value: Any) -> bool:
        """
        Return True if value represents "not set".

        0, 0.0, and False are not empty. They are valid user-supplied values. Only
        None, empty strings, empty lists, and empty dicts qualify.

        Note:
          Identical logic to other GUI interface builders so dependency behaviour is
          consistent across frontends?

        Params:
          value: Raw value from _get_widget_value
          returns: Whether the value should be treated as absent
        """
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and not value:
            return True

        return False
