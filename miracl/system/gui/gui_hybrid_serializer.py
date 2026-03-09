"""
miracl_gui_serializer
=====================

Converts :class:`~miracl.system.datamodels.ResolvedMiraclObj` instances
produced by :class:`~miracl.system.registry.RegistryIntrospector` into a
:class:`~miracl.system.gui.gui_parser_contracts.GuiSchema` — the validated
Pydantic model that any GUI builder consumes.

**Single responsibility**

This module contains exactly one public class,
:class:`MiraclGUISerializer`, with one public method,
:meth:`~MiraclGUISerializer.serialize`.  It reads the registry output,
routes each argument to either the visible (widget) or hidden (INTERNAL)
collection, resolves inter-argument dependencies to UUID strings, and
assembles a fully validated :class:`GuiSchema`.

**Frontend agnosticism**

The serializer has no knowledge of Qt, Gradio, or any other rendering
technology.  :attr:`~gui_parser_contracts.GuiFieldSpec.extensions` carries
the full ``gui_extensions`` dict from each
:class:`~miracl.system.datamodels.ResolvedMiraclObj` with **all** frontend
keys intact.  Each builder reads only its own key::

    qt_ext     = spec.extensions.get("qt", {})
    gradio_ext = spec.extensions.get("gradio", {})

**Routing logic**

Each :class:`~miracl.system.datamodels.ResolvedMiraclObj` in the input dict
is routed as follows::

    resolved is None          ──►  skip  (DISABLED — filtered by introspector)
    resolved.gui_hidden=True  ──►  GuiHiddenArg  (no widget; UUID still required)
    resolved.gui_hidden=False ──►  GuiFieldSpec  (widget rendered in a tab)

INTERNAL arguments (``gui_hidden=True``) must appear in the builder's output
dict so the workflow engine can inject their values via ``data_flow`` UUID
references.  See :class:`~gui_parser_contracts.GuiHiddenArg` for the full
contract.

**widget_type is mandatory**

:meth:`MiraclGUISerializer._to_field_spec` raises
:class:`~gui_parser_contracts.GuiSerializationError` if ``widget_type`` is
``None``.  :class:`~gui_parser_contracts.GuiFieldSpec` additionally validates
the value as a :class:`~gui_parser_contracts.WidgetType` enum member at model
construction time.  This double guard means invalid widget types are caught
immediately at serialization, before any builder code runs.

**Tab ordering**

Tabs are ordered by
:class:`~miracl.system.enums.enums_base_modules.CliGroup` enum declaration
order — deterministic regardless of which module the serializer happens to
encounter first during introspection.
:data:`~gui_parser_contracts.UNGROUPED_TAB_KEY` always sorts last.

**Dependency resolution**

``depends_on`` and ``conflicts_with`` on
:class:`~miracl.system.datamodels.ResolvedMiraclObj` are stored as
**attribute name strings** in the registry (e.g. ``["input_folder"]``).
The serializer resolves these to **UUID strings** before they reach the
builder, using a ``(module, name) → UUID`` map built upfront from the full
``resolved_objects`` dict.

Resolution is scoped to the same module — ``depends_on`` in MIRACL always
refers to a sibling argument in the same module, never a cross-module
reference.

If a name cannot be resolved, :class:`~gui_parser_contracts.GuiSerializationError`
is raised immediately.  There is **no silent fallback** — a typo in a
registry config file must be caught at serialization time, not as a
mysterious widget-wiring failure inside the builder.

**Label convention**

:attr:`~gui_parser_contracts.GuiFieldSpec.label` is ``List[str]`` and is
**never flattened**:

* ``label[0]`` — the string displayed next to the widget.
* ``label[1:]`` — supplementary strings shown as a tooltip on hover.

The same convention applies to ``additional_labels``.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
from pydantic import ValidationError
from miracl.system.datamodels import miraclobj_enums as internal
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.logger import get_logger
from miracl.system.gui.gui_hybrid_serializer_builder_contract import (
    UNGROUPED_TAB_KEY,
    GuiFieldSpec,
    GuiHiddenArg,
    GuiMeta,
    GuiRangeProps,
    GuiSchema,
    GuiSerializationError,
    GuiTab,
    GuiTabMeta,
    GuiTextProps,
    GuiChoicesProps,
    WidgetType as ContractWidgetType,
    GuiWidgetProps,
)

logger = get_logger(__name__)

#: Tuple of Python types that are natively JSON-serialisable.
#: Choice values of these types are stored as-is in :attr:`GuiFieldSpec.choices`.
#: Anything outside this set is cast to ``str`` to guarantee that
#: ``model_dump_json()`` will not raise a ``TypeError``.
_JSON_PRIMITIVES = (int, float, str, bool)

WIDGET_MAPPING = {
    internal.WidgetType.LINE_EDIT: ContractWidgetType.LINE_EDIT,
    internal.WidgetType.SPINBOX: ContractWidgetType.SPINBOX,
    internal.WidgetType.DOUBLE_SPINBOX: ContractWidgetType.SPINBOX,
    internal.WidgetType.DROPDOWN: ContractWidgetType.COMBO_BOX,
    internal.WidgetType.PATH_INPUT: ContractWidgetType.PATH_INPUT,
}


class MiraclGUISerializer:
    """
    Converts :class:`~miracl.system.registry.RegistryIntrospector` output
    into a frontend-agnostic :class:`~gui_parser_contracts.GuiSchema`.

    This is the only class in this module.  Instantiate it once and call
    :meth:`serialize` with the introspector's output dictionaries.

    **Typical usage**::

        serializer = MiraclGUISerializer()

        schema = serializer.serialize(
            resolved_objects=introspector.get_modules_as_dict(),
            meta=introspector.get_meta(),
        )

    **Per-module filtering** (useful when one workflow spans multiple modules
    and you want to render each module's arguments in a separate window)::

        schema = serializer.serialize(
            resolved_objects=module_objects,
            meta=meta_block,
            module_filter="clar_allen",
        )

    **JSON round-trip** (used by the planned save/load session feature)::

        json_str = schema.model_dump_json(indent=2)
        schema   = GuiSchema.model_validate_json(json_str)
    """

    def __init__(self) -> None:
        logger.info("Initialized GUI serializer")

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def serialize(
        self,
        resolved_objects: Dict[str, Dict[str, Any]],
        meta: Any,
        module_filter: Optional[str] = None,
    ) -> GuiSchema:
        """
        Convert :class:`~miracl.system.registry.RegistryIntrospector` output
        into a validated :class:`~gui_parser_contracts.GuiSchema`.

        This method performs the following steps in order:

        1. **Build the dependency id_map** — constructs a
           ``(module, name) → UUID`` lookup table from all non-``None``
           :class:`~miracl.system.datamodels.ResolvedMiraclObj` instances.
           This is done *before* the main loop so that ``depends_on`` and
           ``conflicts_with`` names can be resolved to UUIDs during field
           spec construction.

        2. **Main serialization loop** — iterates every
           :class:`~miracl.system.datamodels.ResolvedMiraclObj` and routes it:

           * ``None`` / disabled → skipped.
           * ``gui_hidden=True`` → :meth:`_to_hidden_arg` →
             :attr:`GuiSchema.hidden`.
           * ``gui_hidden=False`` → :meth:`_to_field_spec` →
             the appropriate :class:`~gui_parser_contracts.GuiTab` in
             ``raw_tabs``.

           The ``by_module`` index is populated inline to avoid a second
           pass over the data after the loop.

        3. **Tab ordering** — ``raw_tabs`` is sorted by
           :class:`~miracl.system.enums.enums_base_modules.CliGroup` enum
           declaration order so the tab sequence is deterministic.
           :data:`~gui_parser_contracts.UNGROUPED_TAB_KEY` always sorts last.

        4. **Schema assembly** — constructs the final
           :class:`~gui_parser_contracts.GuiSchema`, which triggers
           :meth:`~gui_parser_contracts.GuiSchema._validate_consistency`
           automatically via Pydantic's ``model_validator``.

        :param resolved_objects: Output of
            ``RegistryIntrospector.get_modules_as_dict()``.
            Shape: ``Dict[ClassName, Dict[attr_name, ResolvedMiraclObj]]``.
        :param meta: ``MetaConfig`` instance from
            ``RegistryIntrospector.get_meta()``.  Contains the registry
            ``_meta`` block (title, help text, runtime hints, etc.).
        :param module_filter: Optional module name string.  When provided,
            only arguments whose ``resolved.module`` matches this value are
            included.  Applied equally to visible and hidden arguments.
            ``None`` (default) includes all modules.
        :returns: A fully validated :class:`~gui_parser_contracts.GuiSchema`
            ready to be passed into any ``MiraclGUIBuilder.build_form()``.
        :rtype: GuiSchema
        :raises GuiSerializationError: If any visible argument is missing
            a ``gui`` block or an explicit ``widget_type``, or if any
            ``depends_on`` / ``conflicts_with`` name cannot be resolved to
            a UUID within its module.
        """
        logger.info(
            "GUI serialization | total_modules=%d | filter=%s",
            len(resolved_objects),
            module_filter or "none",
        )

        # ── Step 1: build the dependency id_map ──────────────────────────
        #
        # Constructed upfront from the *full* resolved_objects (ignoring
        # module_filter) so that every sibling argument in a module is
        # resolvable even if the filter excludes some of them from the
        # rendered schema.  Resolution is scoped to (module, name) pairs —
        # depends_on in MIRACL always refers to a sibling in the same module.
        id_map: Dict[tuple, str] = {
            (res.module, res.name): str(res.id)
            for attrs in resolved_objects.values()
            for res in attrs.values()
            if res is not None
        }
        logger.debug("Built dependency id_map | entries=%d", len(id_map))

        # ── Step 2: main serialization loop ──────────────────────────────
        #
        # raw_tabs:  tab_key str  ──►  (GuiTabMeta, List[GuiFieldSpec])
        # The by_module index is populated here inline to avoid a
        # second O(N) pass after the loop completes.
        raw_tabs: Dict[str, tuple] = {}
        hidden: List[GuiHiddenArg] = []
        by_module: Dict[str, List[str]] = {}

        total_visible = 0
        total_hidden = 0

        for class_name, attrs in resolved_objects.items():
            logger.debug(
                "Serializing module | class=%s | arg_count=%d",
                class_name,
                len(attrs),
            )

            for resolved in attrs.values():
                if resolved is None:
                    continue  # DISABLED — already filtered by introspector

                if module_filter and resolved.module != module_filter:
                    continue

                if resolved.gui_hidden:
                    # INTERNAL argument — no widget rendered; UUID slot still
                    # required in the builder's output dict.
                    hidden.append(self._to_hidden_arg(resolved))
                    total_hidden += 1
                else:
                    # Visible argument — convert to GuiFieldSpec and assign
                    # to the appropriate tab bucket.
                    spec = self._to_field_spec(
                        resolved,
                        id_map,
                        class_name,
                    )
                    tab_key = spec.tab_label

                    if tab_key not in raw_tabs:
                        # First argument encountered for this tab — create the
                        # bucket with its GuiTabMeta header.
                        raw_tabs[tab_key] = (
                            self._make_tab_meta(resolved.cli.group),
                            [],
                        )

                    raw_tabs[tab_key][1].append(spec)
                    by_module.setdefault(spec.module, []).append(spec.dest)
                    total_visible += 1

        # ── Step 3: sort tabs by CliGroup enum declaration order ──────────
        #
        # Without explicit sorting, tab order would depend on which module
        # the introspector happened to process first — non-deterministic
        # across Python versions and registry changes.  Sorting by enum
        # position guarantees a stable, predictable tab sequence.
        # UNGROUPED_TAB_KEY is assigned a sort position of len(cli_group_order)
        # which is always one past the last real group, placing it last.
        cli_group_order = {g.label: i for i, g in enumerate(CliGroup)}

        def _tab_sort_key(tab_key: str) -> int:
            return cli_group_order.get(tab_key, len(cli_group_order))

        final_tabs: Dict[str, GuiTab] = {
            tab_key: GuiTab(tab_meta=tab_meta, args=args)
            for tab_key, (tab_meta, args) in sorted(
                raw_tabs.items(), key=lambda item: _tab_sort_key(item[0])
            )
        }

        # ── Step 4: assemble and validate the schema ──────────────────────
        #
        # GuiSchema's model_validator (_validate_consistency) runs
        # automatically here, checking cross-field references.
        schema = GuiSchema(
            meta=self._serialize_meta(meta),
            tabs=final_tabs,
            hidden=hidden,
            by_module=by_module,
        )

        logger.success(
            "GUI serialization complete | visible=%d | hidden=%d | tabs=%s",
            total_visible,
            total_hidden,
            list(final_tabs.keys()),
        )

        return schema

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_default(value: Any) -> Any:
        """
        Cast ``pathlib.Path``-like default values to ``str`` for JSON
        round-trip safety.

        Pydantic's ``model_dump_json()`` cannot serialise ``Path`` objects.
        Any value that implements ``__fspath__`` (the path-like protocol) is
        cast to its string representation.  All other values are returned
        unchanged.

        This helper is called for both visible argument defaults (in
        :meth:`_to_field_spec`) and hidden argument defaults (in
        :meth:`_to_hidden_arg`) to centralise the logic in one place.

        :param value: The raw default value from the registry.
        :returns: ``str(value)`` if ``value`` is path-like, otherwise
            ``value`` unchanged.
        :rtype: Any
        """
        return str(value) if hasattr(value, "__fspath__") else value

    @staticmethod
    def _normalize_choice(value: Any) -> Any:
        """
        Preserve JSON-safe primitive choice values as-is; cast everything
        else to ``str``.

        :data:`_JSON_PRIMITIVES` (``int``, ``float``, ``str``, ``bool``)
        survive JSON round-trip without type loss.  Any other type — for
        example a Python ``Enum`` member — is cast to ``str`` to prevent
        ``model_dump_json()`` from raising a ``TypeError``.

        This preserves the original type where possible so the builder
        can render ``int`` choices as integers (useful for spinboxes)
        rather than forcing everything through a string coercion path.

        :param value: One element from ``resolved.cli.choices``.
        :returns: The original value if it is a JSON primitive, otherwise
            ``str(value)``.
        :rtype: Any
        """
        return value if isinstance(value, _JSON_PRIMITIVES) else str(value)

    @staticmethod
    def _serialize_meta(meta: Any) -> GuiMeta:
        """
        Forward the registry ``_meta`` block into a :class:`~gui_parser_contracts.GuiMeta`
        model.

        Uses ``getattr`` with safe defaults for all optional fields so this
        method remains robust against:

        * Partial ``MetaConfig`` objects used in unit tests.
        * Future additions to ``MetaConfig`` that are not yet present in
          older registry configs.

        ``module`` and ``command`` are accessed directly (without
        ``getattr``) because the schema contract requires them to be present
        on every ``MetaConfig``.

        CLI usage examples are intentionally **excluded** — command-line
        invocation strings have no meaning in a GUI context.

        :param meta: ``MetaConfig`` instance from
            ``RegistryIntrospector.get_meta()``.
        :returns: A populated :class:`~gui_parser_contracts.GuiMeta` model.
        :rtype: GuiMeta
        """
        return GuiMeta(
            module=meta.module,
            command=meta.command,
            help=getattr(meta, "help", None),
            extended_help=getattr(meta, "extended_help", None),
            docs_url=getattr(meta, "docs_url", None),
            experimental=getattr(meta, "experimental", False),
            deprecated=getattr(meta, "deprecated", False),
            deprecation_message=getattr(meta, "deprecation_message", None) or None,
            version=getattr(meta, "version", None),
            requires_gpu=getattr(meta, "requires_gpu", False),
            min_memory_gb=getattr(meta, "min_memory_gb", None),
            estimated_runtime=getattr(meta, "estimated_runtime", None),
        )

    @staticmethod
    def _serialize_props(resolved: Any) -> GuiWidgetProps:
        """
        Extract ``GuiWidgetSpecifics`` from a
        :class:`~miracl.system.datamodels.ResolvedMiraclObj` and repack it
        into a :class:`~gui_parser_contracts.GuiWidgetProps` model.

        Only sub-models that are explicitly declared in the registry config
        (i.e. non-``None`` on the source ``widget_specifics``) are populated.
        Sub-models for other widget types remain ``None`` so the builder can
        distinguish "not configured" from "configured to zero/empty".

        .. note::
            By the time this method is called, the ``gui`` block on
            ``resolved`` is **guaranteed non-None** — :meth:`_to_field_spec`
            validates this with a :class:`~gui_parser_contracts.GuiSerializationError`
            guard before ever calling ``_serialize_props``.  The only
            remaining guard here is for ``widget_specifics is None`` (when
            a ``gui`` block exists but declares no ``props``).

        :param resolved: The :class:`~miracl.system.datamodels.ResolvedMiraclObj`
            whose ``gui.base.props`` is to be serialised.
        :returns: A :class:`~gui_parser_contracts.GuiWidgetProps` instance.
            All sub-model fields default to ``None`` for props that were not
            declared.
        :rtype: GuiWidgetProps
        """
        widget_specifics = resolved.gui.base.props

        if widget_specifics is None:
            # gui block exists but no props were declared — return empty props.
            return GuiWidgetProps()

        range_props: Optional[GuiRangeProps] = None
        text_props: Optional[GuiTextProps] = None
        choices_props: Optional[GuiChoicesProps] = None

        if widget_specifics.range is not None:
            r = widget_specifics.range
            range_props = GuiRangeProps(
                min_val=r.min_val,
                max_val=r.max_val,
                increment_val=r.increment_val,
                nr_decimals=r.nr_decimals,
            )

        if widget_specifics.text is not None:
            t = widget_specifics.text
            text_props = GuiTextProps(
                input_restrictions=(
                    # Serialise the InputRestrictionType enum member to its
                    # string value so the model is JSON-safe.
                    t.input_restrictions.value
                    if t.input_restrictions is not None
                    else None
                )
            )

        if widget_specifics.choices is not None:
            c = widget_specifics.choices
            choices_props = GuiChoicesProps(
                vals=c.vals,
                default_val=c.default_val,
            )

        return GuiWidgetProps(
            range=range_props,
            text=text_props,
            choices=choices_props,
        )

    @staticmethod
    def _make_tab_meta(cli_group: Optional[CliGroup]) -> GuiTabMeta:
        """
        Construct a :class:`~gui_parser_contracts.GuiTabMeta` from a
        :class:`~miracl.system.enums.enums_base_modules.CliGroup` enum member.

        For arguments with no ``cli.group`` (i.e. ``cli_group is None``),
        returns a blank :class:`~gui_parser_contracts.GuiTabMeta` with the
        :data:`~gui_parser_contracts.UNGROUPED_TAB_KEY` as the label and an
        empty description string.

        :param cli_group: The ``CliGroup`` enum member for this argument's
            tab, or ``None`` if the argument is ungrouped.
        :returns: A :class:`~gui_parser_contracts.GuiTabMeta` with label and
            description populated from the enum, or a blank meta for
            ungrouped arguments.
        :rtype: GuiTabMeta
        """
        if cli_group is None:
            return GuiTabMeta(label=UNGROUPED_TAB_KEY, description="")
        return GuiTabMeta(
            label=cli_group.label,
            description=cli_group.description,
        )

    @staticmethod
    def _to_hidden_arg(resolved: Any) -> GuiHiddenArg:
        """
        Convert an INTERNAL :class:`~miracl.system.datamodels.ResolvedMiraclObj`
        (``gui_hidden=True``) into a :class:`~gui_parser_contracts.GuiHiddenArg`.

        Only three fields are needed for a hidden arg:

        * :attr:`~gui_parser_contracts.GuiHiddenArg.dest` — the UUID string
          the builder emits in its output dict.
        * :attr:`~gui_parser_contracts.GuiHiddenArg.name` — the attribute
          name, kept for logging and debugging.
        * :attr:`~gui_parser_contracts.GuiHiddenArg.default` — the
          placeholder value the builder emits (the workflow engine overwrites
          this at runtime).

        The default is passed through :meth:`_normalize_default` to ensure
        path-like values are cast to ``str`` for JSON safety.

        :param resolved: A :class:`~miracl.system.datamodels.ResolvedMiraclObj`
            whose ``gui_hidden`` flag is ``True``.
        :returns: A minimal :class:`~gui_parser_contracts.GuiHiddenArg`.
        :rtype: GuiHiddenArg
        """
        logger.debug(
            "Routing INTERNAL argument to hidden | id=%s | name=%s",
            resolved.id,
            resolved.name,
        )
        return GuiHiddenArg(
            dest=str(resolved.id),
            name=resolved.name,
            default=MiraclGUISerializer._normalize_default(resolved.cli.default),
        )

    @staticmethod
    def _resolve_deps(
        names: Optional[List[str]],
        module: str,
        id_map: Dict[tuple, str],
        field: str,
        owner_name: str,
    ) -> Optional[List[str]]:
        """
        Resolve a list of sibling argument **name strings** to **UUID strings**
        using the pre-built ``id_map``.

        The registry stores ``depends_on`` and ``conflicts_with`` as lists of
        attribute names (e.g. ``["input_folder", "output_folder"]``).  The GUI
        builder operates entirely on UUID strings (``dest``).  This method
        bridges the gap so the builder never has to scan the schema to find
        which :class:`~gui_parser_contracts.GuiFieldSpec` owns a given name.

        **Resolution scope**

        Lookup keys are ``(module, name)`` tuples.  This scopes resolution to
        sibling arguments within the same module.  ``depends_on`` in MIRACL is
        always a same-module reference — cross-module dependencies are handled
        at the workflow level, not the argument level.

        **Fail-loud policy**

        If a name cannot be resolved, :class:`~gui_parser_contracts.GuiSerializationError`
        is raised immediately with a message that identifies the owning
        argument, the module, the unresolvable name, and a remediation hint.
        There is **no silent fallback** — passing raw name strings through to
        the builder would cause a confusing wiring failure at widget render
        time rather than a clear error at serialization time.

        :param names: Raw ``depends_on`` or ``conflicts_with`` list from the
            registry, or ``None`` / empty list if no dependencies are declared.
        :param module: Module name of the argument that declares the
            dependency.  Used as the first element of the ``id_map`` lookup
            key.
        :param id_map: Pre-built ``(module, name) → UUID string`` dict
            covering all non-``None`` :class:`~miracl.system.datamodels.ResolvedMiraclObj`
            instances in the current serialization run.
        :param field: Name of the field being resolved (``"depends_on"`` or
            ``"conflicts_with"``).  Used in error messages only.
        :param owner_name: Attribute name of the argument that declared the
            dependency (e.g. ``"ctn_down"``).  Used in error messages only.
        :returns: List of UUID strings in the same order as ``names``, or
            ``None`` if ``names`` is ``None`` or empty.
        :rtype: list[str] or None
        :raises GuiSerializationError: If any name in ``names`` is not found
            in ``id_map`` for the given ``module``.
        """
        if not names:
            return None

        resolved_uuids: List[str] = []
        for name in names:
            uuid = id_map.get((module, name))
            if uuid is None:
                raise GuiSerializationError(
                    f"'{owner_name}' (module='{module}') has {field}=['{name}'] "
                    f"but no argument named '{name}' exists in module '{module}'. "
                    f"Check for typos in the registry config."
                )
            resolved_uuids.append(uuid)

        return resolved_uuids

    @staticmethod
    def _format_gui_error(
        title: str,
        message: Any,
        resolved: Any,
        class_name: str,
        solution: str = None,
    ) -> str:
        """
        Internal helper to create a structured diagnostic dashboard for
        GUI-related errors.
        """
        lines = [
            f"\n{'=' * 60}",
            f"{title.upper()}",
            f"{'-' * 60}",
            f"Class:    {class_name}",
            f"Argument: {resolved.name}",
            f"Module:   {resolved.module}",
            f"Group:    {resolved.module_group}",
            f"ID:       {resolved.id}",
            f"{'-' * 60}",
            f"Details:  {message}",
        ]

        if solution:
            lines.append(f"Solution: {solution}")

        lines.append(f"{'=' * 60}")
        return "\n".join(lines)

    @classmethod
    def _to_field_spec(
        cls,
        resolved: Any,
        id_map: Dict[tuple, str],
        class_name: str,
    ) -> GuiFieldSpec:
        """
        Convert a visible :class:`~miracl.system.datamodels.ResolvedMiraclObj`
        (``gui_hidden=False``) into a fully populated
        :class:`~gui_parser_contracts.GuiFieldSpec`.

        This is the primary per-argument conversion method.  It performs the
        following transformations:

        * **Guards** — raises :class:`~gui_parser_contracts.GuiSerializationError`
          immediately if the ``gui`` block is absent or ``widget_type`` is
          ``None``.  Both are configuration errors that must be fixed in the
          registry before the GUI can render the argument.
        * **Tab routing** — derives ``tab_label`` from
          ``resolved.cli.group.label``, or falls back to
          :data:`~gui_parser_contracts.UNGROUPED_TAB_KEY`.
        * **Type extraction** — passes ``resolved.cli.obj_type.python_type``
          directly to :attr:`~gui_parser_contracts.GuiFieldSpec.value_type`;
          the :meth:`~gui_parser_contracts.GuiFieldSpec._validate_value_type`
          field validator normalises it to a ``JSONType`` string.
        * **Default normalisation** — passes the default through
          :meth:`_normalize_default` to cast path-like values to ``str``.
        * **Choice normalisation** — passes each choice through
          :meth:`_normalize_choice` to preserve JSON-safe primitives and cast
          everything else to ``str``.
        * **Dependency resolution** — calls :meth:`_resolve_deps` for both
          ``depends_on`` and ``conflicts_with``, converting attribute name
          strings to UUID strings.  Raises loudly on any unresolvable name.
        * **Extensions passthrough** — forwards ``resolved.gui_extensions``
          verbatim (all frontend keys intact).

        :param resolved: The :class:`~miracl.system.datamodels.ResolvedMiraclObj`
            to convert.  Must have ``gui_hidden=False``.
        :param id_map: Pre-built ``(module, name) → UUID string`` map used
            by :meth:`_resolve_deps` to resolve dependency names to UUIDs.
        :returns: A fully populated, immutable
            :class:`~gui_parser_contracts.GuiFieldSpec`.
        :rtype: GuiFieldSpec
        :raises GuiSerializationError:
            * If ``resolved.gui`` is ``None`` (no ``gui`` block declared).
            * If ``resolved.gui.base.widget_type`` is ``None``.
            * If any ``depends_on`` or ``conflicts_with`` name cannot be
              resolved to a UUID within the same module.
        """
        logger.debug(
            "Serializing visible argument | id=%s | name=%s",
            resolved.id,
            resolved.name,
        )

        # Guard 1: every visible argument must declare a gui block.
        # INTERNAL arguments (gui_hidden=True) are allowed to omit it —
        # they are routed to _to_hidden_arg before reaching this method.
        # if resolved.gui is None:
        #     raise GuiSerializationError(
        #         f"'{resolved.name}' (module='{resolved.module}') has no 'gui' block. "
        #         f"All visible arguments must declare a gui block."
        #     )
        if resolved.gui is None:
            msg = cls._format_gui_error(
                title="MISSING GUI CONFIGURATION",
                message="This argument is visible but has no 'gui' block declared.",
                resolved=resolved,
                class_name=class_name,
                solution="Add a gui block or set gui_hidden=True in the registry.",
            )
            raise GuiSerializationError(msg)

        gui_base = resolved.gui.base

        # Guard 2: widget_type must always be explicitly declared.
        # The builder has no fallback rendering path for an unknown widget type —
        # an omission here would cause a silent None widget at render time.
        # if gui_base.widget_type is None:
        #     raise GuiSerializationError(
        #         f"'{resolved.name}' (module='{resolved.module}', "
        #         f"module_group='{resolved.module_group}') is missing 'widget_type'. "
        #         f"Widget types must always be declared explicitly — "
        #         f"the builder has no fallback rendering for an unknown widget type."
        #     )
        if gui_base.widget_type is None:
            msg = cls._format_gui_error(
                title="MISSING WIDGET TYPE",
                message="Widget types must always be declared explicitly.",
                resolved=resolved,
                class_name=class_name,
                solution="Add widget_type=WidgetType.SPINBOX (or similar) to the gui block.",
            )
            raise GuiSerializationError(msg)

        logger.debug(
            "Tab routing | name=%s | gui.base.group=%s | cli.group.label=%s",
            resolved.name,
            resolved.gui.base.group if resolved.gui else None,
            resolved.cli.group.label if resolved.cli.group else None,
        )

        # 1. Highest Priority: The explicit GUI group string override
        if resolved.gui and resolved.gui.base.group:
            tab_label = resolved.gui.base.group.label

        # 2. Second Priority: The CLI group Enum label (resolved by flow)
        elif resolved.cli.group is not None:
            tab_label = resolved.cli.group.label

        # 3. Lowest Priority: The Ungrouped Sentinel
        else:
            tab_label = UNGROUPED_TAB_KEY

        # Extract the Python type for this argument.  The GuiFieldSpec field
        # validator (_validate_value_type) accepts a raw type object and
        # normalises it to a JSONType string automatically — no manual
        # conversion is needed here.
        value_type = (
            resolved.cli.obj_type.python_type
            if resolved.cli.obj_type is not None
            else None
        )

        # Normalise choices: preserve JSON-safe primitives, cast everything
        # else to str.  This avoids type loss for integer/float choices while
        # still protecting against non-serialisable enum members or objects.
        raw_choices = resolved.cli.choices
        choices = (
            [cls._normalize_choice(c) for c in raw_choices] if raw_choices else None
        )

        internal_type = resolved.gui.base.widget_type
        contract_widget_type = WIDGET_MAPPING.get(internal_type)
        if contract_widget_type is None:
            msg = cls._format_gui_error(
                title="UNMAPPED WIDGET TYPE",
                message=f"Internal widget type '{internal_type}' has no entry in WIDGET_MAPPING.",
                resolved=resolved,
                class_name=class_name,
                solution=f"Add '{internal_type}' to the WIDGET_MAPPING dict in {Path(__file__).name}.",
            )
            raise GuiSerializationError(msg)

        try:
            spec = GuiFieldSpec(
                dest=str(resolved.id),
                name=resolved.name,
                registry_class=class_name,
                module=resolved.module,
                module_group=resolved.module_group,
                tab_label=tab_label,
                label=gui_base.label,  # List[str] - never flattened
                help_text=resolved.cli.help,
                additional_labels=gui_base.additional_labels,
                widget_type=contract_widget_type,
                value_type=value_type,
                default=cls._normalize_default(resolved.cli.default),
                required=resolved.cli.required or False,
                choices=choices,
                order=gui_base.order,
                props=cls._serialize_props(resolved),
                extensions=resolved.gui_extensions
                or {},  # full dict, all frontend keys
                depends_on=cls._resolve_deps(
                    resolved.depends_on,
                    resolved.module,
                    id_map,
                    field="depends_on",
                    owner_name=resolved.name,
                ),
                conflicts_with=cls._resolve_deps(
                    resolved.conflicts_with,
                    resolved.module,
                    id_map,
                    field="conflicts_with",
                    owner_name=resolved.name,
                ),
                deprecated=resolved.deprecated,
            )

            logger.debug(
                "Serialized visible field | dest=%s | widget_type=%s | tab_label=%s",
                spec.dest,
                spec.widget_type,
                spec.tab_label,
            )

            return spec
        except ValidationError as e:
            msg = cls._format_gui_error(
                title="GUI CONTRACT VIOLATION",
                message=e,
                resolved=resolved,
                class_name=class_name,
                solution="Ensure all GUI fields match the Pydantic Contract (check Enums and Types).",
            )
            raise GuiSerializationError(msg) from None
