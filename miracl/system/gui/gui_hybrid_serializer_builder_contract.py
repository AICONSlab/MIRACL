"""
gui_parser_contracts
====================

Shared data models (the "contract") between :class:`MiraclGUISerializer` and
any GUI builder implementation (PyQt, Gradio, etc.).

**Purpose**

This file defines the formal agreement between two parties:

* **Producer** — :class:`~miracl.system.gui.miracl_gui_serializer.MiraclGUISerializer`
  reads the registry and produces a :class:`GuiSchema`.
* **Consumer** — any ``MiraclGUIBuilder`` subclass reads the :class:`GuiSchema`
  and renders widgets.

Neither party needs to know the internal details of the other.  If the
serializer changes how it groups tabs, the builder is unaffected as long as
the :class:`GuiSchema` is still valid.  If the builder changes how it renders
spinboxes, the serializer is unaffected.

**Why Pydantic BaseModel with frozen=True?**

All models here inherit from ``pydantic.BaseModel`` with ``frozen=True``.
This provides three guarantees:

1. **Runtime validation** — invalid field values are caught the moment the
   model is constructed, not silently later inside the builder.
2. **JSON round-trip** — every model can be serialised to JSON and
   deserialised back without data loss, enabling the planned save/load
   feature::

       json_str = schema.model_dump_json(indent=2)
       schema   = GuiSchema.model_validate_json(json_str)

3. **Immutability** — builders receive a schema they cannot accidentally
   mutate.  Any attempt to assign a field raises ``TypeError``.

**Procedural data flow**

The overall pipeline is strictly one-way::

    RegistryIntrospector
        │
        │  get_modules_as_dict()  ──►  Dict[str, Dict[str, ResolvedMiraclObj]]
        │  get_meta()             ──►  MetaConfig
        ▼
    MiraclGUISerializer.serialize()
        │
        │  GuiSchema  (defined in this file)
        ▼
    MiraclGUIBuilder.build_form()       ◄── PyQtGuiBuilder  OR  GradioGuiBuilder
        │
        │  user fills widgets, clicks Run
        ▼
    Dict[str, Any]  (keys: UUID strings, values: user-supplied OR default values)
        │
        ▼
    deserialize_parsed_args_to_objects()

The builder's output ``dict`` is the **exact shape** that
``deserialize_parsed_args_to_objects`` expects — an identical UUID-keyed
contract to the ``argparse.Namespace`` produced on the CLI path.

**Tab grouping and ordering**

Tabs are sourced from :attr:`ResolvedMiraclObj.cli.group` (a
:class:`~miracl.system.enums.enums_base_modules.CliGroup` enum member).
One :class:`GuiTab` is created per distinct ``CliGroup`` encountered during
serialization.  Arguments whose ``cli.group`` is ``None`` are collected under
the sentinel key :data:`UNGROUPED_TAB_KEY`.

Tab order follows the declaration order of the ``CliGroup`` enum itself — not
the order in which modules happen to be introspected.  This guarantees a
deterministic tab sequence regardless of which module the serializer processes
first.  :data:`UNGROUPED_TAB_KEY` always sorts last.

**Argument ordering within a tab**

Arguments appear in class-attribute declaration order as returned by the
introspector.  :attr:`GuiFieldSpec.order` is forwarded verbatim for the
builder to use for finer-grained sorting if desired; the serializer does not
sort within tabs.

**Label convention**

:attr:`GuiFieldSpec.label` is ``List[str]`` and is **never flattened**. It's a ordered
list of display labels for this widget; each rendered as a separate label row or
concatenated depending on the builder.


:attr:`GuiFieldSpec.additional_labels` follows the same convention.

**Frontend-specific extensions**

:attr:`GuiFieldSpec.extensions` carries the *full* ``gui_extensions`` dict
verbatim from :class:`ResolvedMiraclObj` — all frontend keys are present
(e.g. ``"qt"``, ``"gradio"``).  Each builder reads **only its own key** and
ignores the rest::

    qt_overrides = spec.extensions.get("qt", {})

The serializer has no knowledge of which frontend will consume the schema.

**INTERNAL arguments and the hidden collection**

Arguments declared with ``source=ArgumentSource.INTERNAL`` have
``gui_hidden=True`` on their :class:`ResolvedMiraclObj`.

On the CLI path, ``argparse.SUPPRESS`` hides them from the help text but they
are still registered in the parser and appear in the parsed ``Namespace``.
The workflow engine injects their values via ``data_flow`` UUID-keyed
references at runtime.

The GUI path preserves this contract through :attr:`GuiSchema.hidden`.  The
builder **must** include every entry from ``hidden`` in its output dict as
``{arg.dest: arg.default}``.  The workflow engine will overwrite these values
before the deserializer runs — but the UUID keys must be present in the dict
or the deserializer will raise in strict mode.

No widget is rendered for hidden args.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# SENTINEL  —  placeholder key for arguments that belong to no CliGroup
# ─────────────────────────────────────────────────────────────────────────────

#: Sentinel string used as the ``GuiSchema.tabs`` key for arguments whose
#: ``cli.group`` is ``None``.
#:
#: A dedicated constant string is used **instead of** ``None`` because the
#: JSON standard requires all object keys to be strings — ``None`` would
#: round-trip through ``model_dump_json`` as the string ``"null"``, creating
#: ambiguity when reloading a saved schema.
#:
#: The leading underscore ensures this key sorts *after* all real
#: ``CliGroup.label`` strings in any alphabetical ordering, keeping
#: ungrouped arguments visually separated at the end of the tab bar.
UNGROUPED_TAB_KEY: str = "_ungrouped"


# ─────────────────────────────────────────────────────────────────────────────
# JSON TYPE ENUM  —  JSON-safe representation of Python argument types
# ─────────────────────────────────────────────────────────────────────────────

# --------------------------------------------------------------------------
# Why three separate structures?
#
# Python's class construction order prevents a single declaration from
# covering all three directions we need:
#
#   1.  JSONType enum  — source of truth; defines the closed set of names.
#   2.  _JSON_TYPE_MAP — JSONType member  ──►  Python type  (forward lookup).
#       Used by JSONType.python_type and by GuiFieldSpec.get_value_type().
#       Cannot be populated during the class body because the enum members
#       don't exist yet while the class is being defined.
#   3.  _PYTHON_TYPE_TO_JSON_VALUE — Python type  ──►  JSONType value string
#       (reverse lookup).  Used by _validate_value_type for O(1) resolution
#       instead of a linear scan over enum members.
#
# Both maps are populated in a single statement after the enum is fully
# defined.  They are private — callers use JSONType.python_type and
# GuiFieldSpec.get_value_type() as the public interface.
# --------------------------------------------------------------------------

#: Forward map: :class:`JSONType` member  ──►  Python ``type`` object.
#: Populated immediately after :class:`JSONType` is defined.
#: Do not access directly — use :attr:`JSONType.python_type` instead.
_JSON_TYPE_MAP: Dict["JSONType", Type] = {}

#: Reverse map: Python ``type`` object  ──►  :class:`JSONType` value string.
#: Populated immediately after :class:`JSONType` is defined.
#: Used internally by :meth:`GuiFieldSpec._validate_value_type` for O(1)
#: lookup.  Do not access directly outside this module.
_PYTHON_TYPE_TO_JSON_VALUE: Dict[Type, str] = {}


class JSONType(str, Enum):
    """
    Closed enumeration of Python types that may appear as
    :attr:`ArgumentType.python_type <miracl.system.datamodels.ArgumentType.python_type>`,
    expressed as JSON-safe string values.

    **Why inherit from** ``str``?

    Inheriting from both ``str`` and ``Enum`` means each member *is* a
    string — ``JSONType.INTEGER == "int"`` evaluates to ``True``.  Pydantic
    serialises these values as plain strings with no additional configuration,
    which is what makes :class:`GuiFieldSpec` fully JSON round-trip safe.

    **Extending this enum**

    If a new :class:`ArgumentType` entry is added whose ``python_type`` is
    not listed here, add a new member to this enum *and* update
    ``_JSON_TYPE_MAP`` and ``_PYTHON_TYPE_TO_JSON_VALUE`` in the ``update``
    calls below.  The :meth:`GuiFieldSpec._validate_value_type` validator
    will raise :class:`GuiSerializationError` at serialization time if an
    unregistered type is encountered, so the omission will be caught early.

    .. note::
        This enum mirrors the pattern used by ``ArgumentType`` and other
        enums in the MIRACL codebase.
    """

    INTEGER = "int"  #: Maps to Python built-in :class:`int`.
    FLOAT = "float"  #: Maps to Python built-in :class:`float`.
    STRING = "str"  #: Maps to Python built-in :class:`str`.
    BOOLEAN = "bool"  #: Maps to Python built-in :class:`bool`.
    LIST = "list"  #: Maps to Python built-in :class:`list`.
    PATH = "Path"  #: Maps to :class:`pathlib.Path` (all subclasses normalised here).

    @property
    def python_type(self) -> Type:
        """
        Resolve this enum member back to the corresponding Python ``type``.

        Uses :data:`_JSON_TYPE_MAP` for the lookup.  The map is guaranteed to
        contain every member because it is populated immediately after this
        class is defined.

        :returns: The Python type corresponding to this ``JSONType`` member,
            e.g. ``JSONType.INTEGER.python_type`` returns ``int``.
        :rtype: type
        """
        return _JSON_TYPE_MAP[self]


# Populate both maps now that all enum members exist.
# _JSON_TYPE_MAP    —  forward:  JSONType  ──►  Python type
# _PYTHON_TYPE_TO_JSON_VALUE  —  reverse:  Python type  ──►  string value
_JSON_TYPE_MAP.update(
    {
        JSONType.INTEGER: int,
        JSONType.FLOAT: float,
        JSONType.STRING: str,
        JSONType.BOOLEAN: bool,
        JSONType.LIST: list,
        JSONType.PATH: Path,
    }
)

_PYTHON_TYPE_TO_JSON_VALUE.update(
    {
        int: JSONType.INTEGER.value,
        float: JSONType.FLOAT.value,
        str: JSONType.STRING.value,
        bool: JSONType.BOOLEAN.value,
        list: JSONType.LIST.value,
        Path: JSONType.PATH.value,
    }
)


# ─────────────────────────────────────────────────────────────────────────────
# WIDGET TYPE ENUM  —  self-documenting set of renderable widget kinds
# ─────────────────────────────────────────────────────────────────────────────


class WidgetType(str, Enum):
    """
    Complete enumeration of widget types that a GUI builder knows how to render.

    **Why define this in the contracts file?**

    Typing :attr:`GuiFieldSpec.widget_type` as ``WidgetType`` (rather than
    plain ``str``) means:

    * Pydantic validates the value at model construction time — an invalid
      widget type string is caught the moment the schema is assembled, not
      when the builder tries to render it.
    * Any developer building a new frontend can see the complete set of valid
      widget types directly from the contract, without consulting the
      serializer or the main datamodel.

    .. warning::
        This enum **must stay in sync** with the ``WidgetType`` enum in the
        main datamodel (``miracl.system.datamodels``).  If a new widget type
        is added there, add the corresponding member here too.
    """

    SPINBOX = "SPINBOX"  #: Integer or float numeric input with up/down arrows.
    LINE_EDIT = "LINE_EDIT"  #: Single-line free-text input field.
    COMBO_BOX = (
        "COMBO_BOX"  #: Drop-down selector populated from ``GuiFieldSpec.choices``.
    )
    PATH_INPUT = (
        "PATH_INPUT"  #: Text field paired with a file/directory browser button.
    )
    CHECKBOX = "CHECKBOX"  #: Boolean toggle (checked = True, unchecked = False).
    SLIDER = "SLIDER"  #: Horizontal drag slider for numeric ranges.
    TEXT_AREA = "TEXT_AREA"  #: Multi-line free-text input.
    DATE_PICKER = "DATE_PICKER"  #: Calendar-based date selection widget.
    COLOR_PICKER = "COLOR_PICKER"  #: Colour swatch that opens a colour chooser dialog.


# ─────────────────────────────────────────────────────────────────────────────
# EXCEPTION  —  named error type for all serialization failures
# ─────────────────────────────────────────────────────────────────────────────


class GuiSerializationError(ValueError):
    """
    Raised by :class:`~miracl.system.gui.miracl_gui_serializer.MiraclGUISerializer`
    when a :class:`~miracl.system.datamodels.ResolvedMiraclObj` is missing
    metadata that the GUI layer requires.

    Inherits from :class:`ValueError` so it behaves like a standard value
    error, but can also be caught specifically::

        try:
            schema = serializer.serialize(resolved_objects, meta)
        except GuiSerializationError as exc:
            logger.error("Schema assembly failed: %s", exc)
            raise

    **Common causes**

    * A visible argument (``gui_hidden=False``) has no ``gui`` block declared
      in its registry config.
    * A visible argument is missing an explicit ``widget_type`` declaration.
    * A ``depends_on`` or ``conflicts_with`` entry references an argument name
      that does not exist in the same module (likely a typo in the config).
    """


# ─────────────────────────────────────────────────────────────────────────────
# META  —  registry metadata forwarded to the GUI help dialog and title bar
# ─────────────────────────────────────────────────────────────────────────────


class GuiMeta(BaseModel):
    """
    Frozen snapshot of the registry ``_meta`` block, shaped for GUI consumption.

    The GUI uses this model in two places:

    * **Window / panel title** — :attr:`command` (and optionally :attr:`module`)
      are used as the window title so the user knows which workflow they are
      configuring.
    * **Help dialog** — all remaining fields are displayed when the user clicks
      the ``Help`` or ``?`` button.  A builder should render them gracefully
      even when optional fields are ``None``.

    .. note::
        CLI usage examples are intentionally **not** included here.  Examples
        such as ``miracl flow conv_reg -i /data`` have no meaning in a GUI
        context where the user interacts via widgets, not a command line.

    :ivar module: Registry module identifier (e.g. ``"flow"``).
        Used as part of the window title.
    :ivar command: Human-readable command name (e.g. ``"conv_reg"``).
        Used as the primary window title.
    :ivar help: One-sentence summary shown at the top of the help dialog.
    :ivar extended_help: Multi-paragraph description shown in the body of
        the help dialog.  May contain newlines.
    :ivar docs_url: URL to the full online documentation page.  The builder
        may render this as a clickable hyperlink.
    :ivar experimental: ``True`` if this workflow/module is not yet considered
        stable.  The builder should display a prominent warning banner.
    :ivar deprecated: ``True`` if this workflow/module has been superseded.
        The builder should display a deprecation warning.
    :ivar deprecation_message: Human-readable explanation of what replaces
        this workflow.  Only meaningful when :attr:`deprecated` is ``True``.
    :ivar version: Version string of the module (e.g. ``"2.0.0"``).
        Shown in the help dialog footer.
    :ivar requires_gpu: ``True`` if the workflow requires a CUDA-capable GPU.
        The builder may display a GPU badge.
    :ivar min_memory_gb: Minimum RAM required as a human-readable string
        (e.g. ``"256GB"``).  Shown in the help dialog footer.
    :ivar estimated_runtime: Indicative runtime as a human-readable string
        (e.g. ``"2-4h"``).  Shown in the help dialog footer.
    """

    model_config = ConfigDict(frozen=True)

    # ── Identity ─────────────────────────────────────────────────────────
    module: str
    command: str

    # ── Primary help content ─────────────────────────────────────────────
    help: Optional[str] = None
    extended_help: Optional[str] = None
    docs_url: Optional[str] = None

    # ── Status flags — drive warning banners in the builder ──────────────
    experimental: bool = False
    deprecated: bool = False
    deprecation_message: Optional[str] = None

    # ── Runtime hints — shown in the help dialog footer ──────────────────
    version: Optional[str] = None
    requires_gpu: bool = False
    min_memory_gb: Optional[str] = None
    estimated_runtime: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# WIDGET PROPS  —  per-widget-type configuration forwarded from the registry
# ─────────────────────────────────────────────────────────────────────────────


class GuiRangeProps(BaseModel):
    """
    Numeric range and step configuration for spinbox and slider widgets.

    All fields are optional — only those explicitly declared in the registry
    config will be non-``None``.  A builder should apply sensible fallbacks
    (e.g. no minimum/maximum bound) for any ``None`` field.

    :ivar min_val: Minimum permitted value, inclusive.
    :ivar max_val: Maximum permitted value, inclusive.
    :ivar increment_val: Step size for each click of an up/down arrow or
        drag increment on a slider.
    :ivar nr_decimals: Number of decimal places to display and accept.
        ``0`` means integer-only input even if the type is ``float``.
    """

    model_config = ConfigDict(frozen=True)

    min_val: Optional[float] = None
    max_val: Optional[float] = None
    increment_val: Optional[float] = None
    nr_decimals: Optional[int] = None


class GuiTextProps(BaseModel):
    """
    Input restriction configuration for line edit widgets.

    Controls what characters or patterns the user is permitted to type.

    :ivar input_restrictions: Serialised value of an ``InputRestrictionType``
        enum member (e.g. ``"INTEGERS_ONLY"``, ``"NO_SPACES"``).  ``None``
        means no restrictions — accept any text.
    """

    model_config = ConfigDict(frozen=True)

    #: Serialised ``InputRestrictionType`` value string, or ``None`` for
    #: unrestricted input.
    input_restrictions: Optional[str] = None


class GuiChoicesProps(BaseModel):
    """
    GUI-layer override labels and default for combo-box / choice widgets.

    When present, these values take precedence over
    :attr:`GuiFieldSpec.choices` for display purposes, allowing the GUI
    to show human-friendly labels (e.g. ``"16-bit unsigned integer"``)
    while the underlying choice value remains a machine-readable string
    (e.g. ``"uint16"``).

    :ivar vals: Ordered list of display labels corresponding 1-to-1 with
        :attr:`GuiFieldSpec.choices`.  ``None`` means use the raw choice
        values as labels.
    :ivar default_val: Display label of the choice that should be selected
        by default.  ``None`` means no GUI-level default override — fall
        back to :attr:`GuiFieldSpec.default`.
    """

    model_config = ConfigDict(frozen=True)

    vals: Optional[List[str]] = None
    default_val: Optional[str] = None


class GuiWidgetProps(BaseModel):
    """
    Container for all widget-specific configuration, flattened from the
    registry's ``GuiWidgetSpecifics`` object.

    Only the sub-models that were explicitly declared in the registry config
    will be non-``None``.  A builder should check each sub-model for
    ``None`` before accessing its fields::

        if spec.props.range is not None:
            spinbox.setMinimum(spec.props.range.min_val or 0)

    :ivar range: Numeric range/step config.  Non-``None`` for ``SPINBOX``
        and ``SLIDER`` widgets.
    :ivar text: Input restriction config.  Non-``None`` for ``LINE_EDIT``
        widgets that restrict character input.
    :ivar choices: Choice display override config.  Non-``None`` for
        ``COMBO_BOX`` widgets that declare GUI-friendly labels.
    """

    model_config = ConfigDict(frozen=True)

    range: Optional[GuiRangeProps] = None
    text: Optional[GuiTextProps] = None
    choices: Optional[GuiChoicesProps] = None


# ─────────────────────────────────────────────────────────────────────────────
# TAB IDENTITY  —  label and description for one rendered tab
# ─────────────────────────────────────────────────────────────────────────────


class GuiTabMeta(BaseModel):
    """
    Identity information for a single GUI tab, sourced from the
    :class:`~miracl.system.enums.enums_base_modules.CliGroup` enum.

    The builder uses this to set the tab title and tooltip without needing
    to import or reference ``CliGroup`` directly.

    :ivar label: Human-readable tab title, sourced from
        ``CliGroup.label`` (e.g. ``"conversion"``, ``"registration"``,
        ``"required"``).  Used as the visible tab header text.
    :ivar description: Longer description sourced from
        ``CliGroup.description``.  Shown as a tooltip when the user hovers
        over the tab header.
    """

    model_config = ConfigDict(frozen=True)

    label: str
    description: str


# ─────────────────────────────────────────────────────────────────────────────
# HIDDEN ARG  —  INTERNAL argument with no widget but a required UUID slot
# ─────────────────────────────────────────────────────────────────────────────


class GuiHiddenArg(BaseModel):
    """
    Minimal representation of an ``INTERNAL`` registry argument.

    INTERNAL arguments are arguments whose value is **not** supplied by the
    user — instead the workflow engine injects them at runtime via
    ``data_flow`` UUID references.  No widget is rendered for these
    arguments.

    **Why does the builder still need to emit them?**

    ``deserialize_parsed_args_to_objects`` expects a dict keyed by UUID
    strings for *every* argument, visible or not.  On the CLI path this dict
    is the ``argparse.Namespace`` — argparse registers INTERNAL args with
    ``dest=str(uuid)`` and ``default=default_value`` so they always appear
    in the Namespace even though they are suppressed in help output.

    The GUI path must replicate this: the builder emits
    ``{arg.dest: arg.default}`` for every entry in :attr:`GuiSchema.hidden`.
    The workflow engine then **overwrites** those defaults with the correct
    runtime values before deserialization runs.

    :ivar dest: UUID string that uniquely identifies this argument across
        the entire registry.  This **must** appear as a key in the builder's
        output dict.
    :ivar name: Human-readable attribute name (e.g. ``"ctn_tiff_folder"``).
        Used for logging and debugging only — the builder does not display it.
    :ivar default: The placeholder value the builder emits for this argument.
        The workflow engine will overwrite it, but it must be JSON-safe so
        that saved schemas can be reloaded correctly.
    """

    model_config = ConfigDict(frozen=True)

    dest: str  # UUID string — must appear as a key in the builder's output dict
    name: str  # human-readable name for logging/debugging only
    default: Optional[Any] = None


# ─────────────────────────────────────────────────────────────────────────────
# FIELD SPEC  —  complete specification for one rendered input widget
# ─────────────────────────────────────────────────────────────────────────────


class GuiFieldSpec(BaseModel):
    """
    Complete specification for one visible input widget in the GUI.

    This is the primary unit the widget factory operates on.  For each
    :class:`GuiFieldSpec` in a :class:`GuiTab`, the builder creates one
    widget, binds it to the spec's :attr:`dest` UUID, and includes the
    widget's value in the output dict when the user clicks Run.

    **The UUID contract**

    :attr:`dest` is the single most important field.  It is ``str(resolved.id)``
    — the same UUID string used as ``dest=`` in the CLI argparse serializer.
    The output dict produced by the builder must use these UUID strings as
    keys.  That dict is passed **directly** to
    ``deserialize_parsed_args_to_objects``, which maps values back to their
    :class:`ResolvedMiraclObj` instances by UUID.

    **Label convention**

    :attr:`label` is ``List[str]`` and is **never flattened**:

    * ``label[0]`` — the string displayed next to the widget.
    * ``label[1:]`` — supplementary strings concatenated and shown as a
      tooltip when the user hovers over the label.

    The same convention applies to :attr:`additional_labels`.

    **value_type storage**

    :attr:`value_type` is stored as a :class:`JSONType` string (e.g.
    ``"int"``, ``"Path"``) rather than as a Python ``type`` object.  This is
    required for JSON round-trip safety — Pydantic cannot serialise
    ``<class 'int'>`` to JSON, but ``"int"`` round-trips perfectly.
    Use :meth:`get_value_type` to recover the real Python type at runtime.

    :ivar dest: UUID string — the key the builder must use in its output
        dict.  Mirrors ``dest=str(resolved.id)`` in the CLI serializer.
    :ivar name: Human-readable attribute name (e.g. ``"ctn_down"``).
        Used for logging and as a fallback label if :attr:`label` is
        ``None``.
    :ivar module: Registry module this argument belongs to
        (e.g. ``"tiff_nii"``).  Used for per-module filtering via
        :meth:`GuiSchema.fields_for_module`.
    :ivar module_group: Sub-group within the module
        (e.g. ``"Mapl3WorkflowConnectors"``).  Forwarded for debugging.
    :ivar tab_label: Key of the :class:`GuiTab` this field belongs to.
        Always a string — either a ``CliGroup.label`` value or
        :data:`UNGROUPED_TAB_KEY`.  Must match a key in
        :attr:`GuiSchema.tabs` (validated by
        :meth:`GuiSchema._validate_consistency`).
    :ivar label: Primary and tooltip labels.  ``label[0]`` is displayed;
        ``label[1:]`` are shown as a hover tooltip.  ``None`` if the
        registry config declared no label.
    :ivar additional_labels: Secondary label group following the same
        ``label[0]`` / ``label[1:]`` convention.  ``None`` if unused.
    :ivar widget_type: :class:`WidgetType` enum member identifying the
        Qt/Gradio widget to render.  Always present — Pydantic rejects
        any value not in the enum.
    :ivar value_type: :class:`JSONType` value string (e.g. ``"int"``,
        ``"Path"``), or ``None`` if the argument type is unknown.
        Use :meth:`get_value_type` to resolve this to a Python ``type``.
    :ivar default: Initial value pre-populated into the widget, or ``None``.
        Path-like values have been cast to ``str`` for JSON safety.
    :ivar required: If ``True``, the builder must prevent the user from
        clicking Run until this widget has a non-empty value.
    :ivar choices: Ordered list of permitted values for combo-box widgets.
        JSON-safe primitives (``int``, ``float``, ``str``, ``bool``) are
        preserved as their original type; other values are cast to ``str``.
        ``None`` for free-input widgets.
    :ivar order: Optional float hint for within-tab ordering.  The
        serializer does not sort — builders may use this for finer control.
    :ivar props: Widget-specific configuration (range, text restrictions,
        choice overrides).  Sub-models are ``None`` for widget types that
        do not use them.
    :ivar extensions: Full ``gui_extensions`` dict from the registry with
        **all** frontend keys intact (e.g.
        ``{"qt": {...}, "gradio": {...}}``).  Each builder reads only its
        own key: ``spec.extensions.get("qt", {})``.
    :ivar depends_on: List of UUID strings identifying arguments that must
        have a value before this widget becomes enabled.  Empty/``None``
        means no dependencies.  These were resolved from attribute name
        strings by the serializer — builders receive UUIDs, not names.
    :ivar conflicts_with: List of UUID strings identifying arguments that,
        when set, should disable or hide this widget.  Resolved from
        attribute name strings by the serializer.
    :ivar deprecated: ``True`` if this specific argument has been
        deprecated.  The builder should render a visual deprecation hint.
    """

    model_config = ConfigDict(frozen=True)

    dest: str
    name: str
    registry_class: str
    module: str
    module_group: str
    tab_label: str = UNGROUPED_TAB_KEY  # always a string — never None
    label: List[str]
    help_text: Optional[str] = None
    additional_labels: Optional[List[str]] = None
    widget_type: WidgetType  # validated by Pydantic — never None

    # Stored as a JSONType value string (e.g. "int", "Path") rather than as
    # a Python type object, because Pydantic cannot serialise type objects to
    # JSON.  Use get_value_type() to recover the real Python type at runtime.
    value_type: Optional[str] = None

    default: Optional[Any] = None
    required: bool = False
    choices: Optional[List[Any]] = None
    order: Optional[float] = None
    props: GuiWidgetProps = GuiWidgetProps()
    extensions: Dict[str, Dict[str, Any]] = {}
    depends_on: Optional[List[str]] = None
    conflicts_with: Optional[List[str]] = None
    deprecated: bool = False

    @field_validator("value_type", mode="before")
    @classmethod
    def _validate_value_type(cls, v: Any) -> Optional[str]:
        """
        Pre-storage validator that normalises ``value_type`` to a
        :class:`JSONType` value string regardless of the input form.

        This validator runs automatically whenever a :class:`GuiFieldSpec`
        is constructed (``mode="before"`` means it runs before Pydantic's
        own type coercion).  It accepts three input forms to keep the
        serializer call-site simple:

        * **Python** ``type`` **object** (e.g. ``int``, ``pathlib.Path``) —
          looked up in :data:`_PYTHON_TYPE_TO_JSON_VALUE` for O(1)
          resolution.  All ``pathlib`` subclasses
          (``PosixPath``, ``WindowsPath``, etc.) are normalised to
          ``JSONType.PATH`` so the stored value is platform-independent.
        * **JSONType enum member** (e.g. ``JSONType.INTEGER``) —
          its ``.value`` string is returned directly.
        * **String** (e.g. ``"int"``) — validated against the known
          :class:`JSONType` values and returned unchanged if valid.
        * ``None`` — passed through unchanged.

        :param v: Raw value passed to the ``value_type`` field during
            model construction.
        :returns: A :class:`JSONType` value string, or ``None``.
        :rtype: str or None
        :raises ValueError: If ``v`` is a type not in
            :data:`_PYTHON_TYPE_TO_JSON_VALUE`, a string not in
            :class:`JSONType`, or an unsupported type altogether.
            Fails loudly so problems are caught at serialization time,
            not silently during schema load.
        """
        if v is None:
            return None

        if isinstance(v, JSONType):
            # Already a JSONType member — return its string value directly.
            return v.value

        if isinstance(v, type):
            # Normalise all pathlib subclasses to PATH regardless of platform.
            # pathlib.PosixPath.__name__ == "PosixPath" and
            # pathlib.WindowsPath.__name__ == "WindowsPath" — neither is
            # registered in _PYTHON_TYPE_TO_JSON_VALUE, so we handle Path
            # subclasses explicitly before the dict lookup.
            if issubclass(v, Path):
                return JSONType.PATH.value
            result = _PYTHON_TYPE_TO_JSON_VALUE.get(v)
            if result is None:
                raise ValueError(
                    f"No JSONType entry for type '{v.__name__}'. "
                    f"Add it to JSONType and the maps before using it as an ArgumentType."
                )
            return result

        if isinstance(v, str):
            try:
                return JSONType(v).value
            except ValueError:
                valid = [m.value for m in JSONType]
                raise ValueError(
                    f"'{v}' is not a valid JSONType value. Valid values: {valid}"
                )

        raise ValueError(
            f"value_type must be a type, JSONType member, or string — got {type(v)}"
        )

    def get_value_type(self) -> Optional[Type]:
        """
        Resolve :attr:`value_type` back to the real Python ``type`` object.

        This is the public accessor for the type stored as a JSON-safe
        string.  Call this whenever you need to coerce a raw user-supplied
        widget value to the correct Python type before passing it to
        ``deserialize_parsed_args_to_objects``::

            vt = spec.get_value_type()
            coerced = vt(raw_user_input) if vt is not None else raw_user_input

        :returns: The Python ``type`` corresponding to :attr:`value_type`,
            e.g. ``int`` for ``"int"``, ``pathlib.Path`` for ``"Path"``.
            Returns ``None`` if :attr:`value_type` is ``None``.
        :rtype: type or None
        """
        if self.value_type is None:
            return None
        return JSONType(self.value_type).python_type


# ─────────────────────────────────────────────────────────────────────────────
# TAB  —  one rendered tab containing an ordered collection of field specs
# ─────────────────────────────────────────────────────────────────────────────


class GuiTab(BaseModel):
    """
    Represents one tab in the GUI, corresponding to one
    :class:`~miracl.system.enums.enums_base_modules.CliGroup`.

    The builder creates one tab widget per entry in :attr:`GuiSchema.tabs`,
    uses :attr:`tab_meta` to set the tab title and tooltip, then iterates
    :attr:`args` to render each field's widget in order.

    :ivar tab_meta: Title and description for this tab, sourced from the
        ``CliGroup`` enum.  See :class:`GuiTabMeta`.
    :ivar args: Ordered list of :class:`GuiFieldSpec` instances for this
        tab, in class-attribute declaration order from introspection.
    """

    model_config = ConfigDict(frozen=True)

    tab_meta: GuiTabMeta
    args: List[GuiFieldSpec]


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA  —  top-level output of the serializer; direct input to the builder
# ─────────────────────────────────────────────────────────────────────────────


class GuiSchema(BaseModel):
    """
    Complete, validated output of
    :meth:`~miracl.system.gui.miracl_gui_serializer.MiraclGUISerializer.serialize`.

    This is the single object passed into ``MiraclGUIBuilder.build_form()``.
    The builder reads everything it needs from here — it never accesses the
    registry or the introspector directly.

    **Frontend agnosticism**

    The schema carries no reference to a specific frontend.
    :attr:`GuiFieldSpec.extensions` contains all frontend keys intact; each
    builder reads only its own key.

    **Consistency guarantees**

    Pydantic's ``model_validator`` runs :meth:`_validate_consistency`
    automatically at construction time.  If any internal cross-reference is
    broken (e.g. a ``tab_label`` that references a non-existent tab key),
    a ``ValueError`` is raised immediately rather than causing a confusing
    failure inside the builder.

    **JSON round-trip**

    The entire schema can be serialised to JSON and reloaded::

        # Save
        Path("schema.json").write_text(schema.model_dump_json(indent=2))

        # Load
        schema = GuiSchema.model_validate_json(Path("schema.json").read_text())

    This enables the planned save/load session feature.

    :ivar meta: Registry metadata for the window title and help dialog.
        See :class:`GuiMeta`.
    :ivar tabs: Ordered ``dict`` mapping tab key strings to :class:`GuiTab`
        instances.  Keys are ``CliGroup.label`` strings for grouped
        arguments, or :data:`UNGROUPED_TAB_KEY` for ungrouped ones.  Ordered
        by ``CliGroup`` enum declaration order; :data:`UNGROUPED_TAB_KEY`
        always last.
    :ivar hidden: List of INTERNAL arguments that require no widget but
        **must** appear in the builder's output dict.
        See :class:`GuiHiddenArg` for the full contract.
    :ivar by_module: Index mapping module name to a list of
        :attr:`GuiFieldSpec.dest` UUID strings for all *visible* fields in
        that module.  Use :meth:`fields_for_module` for convenient access.
    """

    model_config = ConfigDict(frozen=True)

    meta: GuiMeta
    tabs: Dict[str, GuiTab]  # keys are always strings — no None keys
    hidden: List[GuiHiddenArg]
    by_module: Dict[str, List[str]]

    @model_validator(mode="after")
    def _validate_consistency(self) -> "GuiSchema":
        """
        Cross-field consistency validator, run automatically by Pydantic
        immediately after the model is constructed.

        Checks two internal cross-references that cannot be enforced by
        individual field types alone:

        1. **tab_label integrity** — every :attr:`GuiFieldSpec.tab_label`
           value must match a key in :attr:`tabs`.  A mismatch would mean a
           field claims to belong to a tab that was never created.
        2. **by_module integrity** — every UUID string listed in
           :attr:`by_module` must correspond to a real
           :attr:`GuiFieldSpec.dest` in :attr:`tabs`.  A stale reference
           would cause :meth:`fields_for_module` to silently return partial
           results.

        :returns: The validated :class:`GuiSchema` instance (``self``).
        :raises ValueError: If either consistency check fails.  The error
            message names the offending field spec and the broken reference
            so the developer can identify the root cause immediately.
        """
        all_field_ids: set = {
            spec.dest for tab in self.tabs.values() for spec in tab.args
        }

        # Check 1: every tab_label back-reference must resolve to a real tab key.
        for tab in self.tabs.values():
            for spec in tab.args:
                if spec.tab_label not in self.tabs:
                    raise ValueError(
                        f"GuiFieldSpec '{spec.name}' has tab_label='{spec.tab_label}' "
                        f"which is not a key in GuiSchema.tabs."
                    )

        # Check 2: every dest ID in by_module must resolve to a real field.
        for module, ids in self.by_module.items():
            unknown = set(ids) - all_field_ids
            if unknown:
                raise ValueError(
                    f"by_module['{module}'] references unknown field dest IDs: {unknown}"
                )

        return self

    @property
    def fields(self) -> List[GuiFieldSpec]:
        """
        Flat ordered list of all visible :class:`GuiFieldSpec` instances
        across all tabs.

        Preserves tab insertion order (which is ``CliGroup`` declaration
        order) and within-tab argument order.  Useful when the builder needs
        to iterate all visible fields without caring about tab boundaries,
        e.g. for bulk validation before enabling the Run button.

        :returns: All visible :class:`GuiFieldSpec` instances in schema order.
        :rtype: list[GuiFieldSpec]
        """
        return [spec for tab in self.tabs.values() for spec in tab.args]

    def fields_for_group(self, group: str) -> List[GuiFieldSpec]:
        """
        Return all visible :class:`GuiFieldSpec` instances belonging to a
        specific tab.

        Convenience accessor so the builder does not need to navigate the
        nested ``tabs[group].args`` structure directly.

        :param group: Tab key string — either a ``CliGroup.label`` value
            (e.g. ``"conversion"``) or :data:`UNGROUPED_TAB_KEY`.
        :returns: Ordered list of :class:`GuiFieldSpec` instances in
            introspection order, or an empty list if ``group`` is not a key
            in :attr:`tabs`.
        :rtype: list[GuiFieldSpec]
        """
        tab = self.tabs.get(group)
        return list(tab.args) if tab else []

    def fields_for_module(self, module: str) -> List[GuiFieldSpec]:
        """
        Return all visible :class:`GuiFieldSpec` instances whose
        :attr:`~GuiFieldSpec.module` matches ``module``.

        Uses the pre-built :attr:`by_module` index for efficient lookup,
        then returns specs in their original schema order.

        Typical use: a multi-module workflow builder that renders each
        module's arguments in a separate panel or section::

            for module_name in schema.by_module:
                specs = schema.fields_for_module(module_name)
                panel = build_module_panel(module_name, specs)

        :param module: Module name string (e.g. ``"tiff_nii"``,
            ``"clar_allen"``).
        :returns: Ordered list of :class:`GuiFieldSpec` instances for that
            module in schema order, or an empty list if the module has no
            visible fields.
        :rtype: list[GuiFieldSpec]
        """
        ids = set(self.by_module.get(module, []))
        return [f for f in self.fields if f.dest in ids]
