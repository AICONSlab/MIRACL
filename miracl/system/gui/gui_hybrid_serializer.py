"""
Code written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Converts miracl.system.datamodels.ResolvedMiraclObj instances produced by
miracl.system.registry.RegistryIntrospector into a
miracl.system.gui.gui_parser_contracts.GuiSchema. The validated Pydantic model that any
GUI builder consumes.
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

_JSON_PRIMITIVES = (int, float, str, bool)

WIDGET_MAPPING = {
    internal.WidgetType.LINE_EDIT: ContractWidgetType.LINE_EDIT,
    internal.WidgetType.SPINBOX: ContractWidgetType.SPINBOX,
    internal.WidgetType.DOUBLE_SPINBOX: ContractWidgetType.DOUBLE_SPINBOX,
    internal.WidgetType.NULLABLE_DOUBLE_SPINBOX: ContractWidgetType.NULLABLE_DOUBLE_SPINBOX,
    internal.WidgetType.COMBO_BOX: ContractWidgetType.COMBO_BOX,
    internal.WidgetType.PATH_INPUT: ContractWidgetType.PATH_INPUT,
    internal.WidgetType.MULTI_LINE_EDIT: ContractWidgetType.MULTI_LINE_EDIT,
}


class MiraclGUISerializer:
    """
    Converts miracl.system.registry.RegistryIntrospector output into a frontend-
    agnostic gui_parser_contracts.GuiSchema.
    """

    def __init__(self) -> None:
        logger.info("Initialized GUI serializer")

    ###################################################################################
    # PUBLIC API
    ###################################################################################

    def serialize(
        self,
        resolved_objects: Dict[str, Dict[str, Any]],
        meta: Any,
        module_filter: Optional[str] = None,
        module_order: Optional[List[str]] = None,
    ) -> GuiSchema:
        """
        Convert miracl.system.registry.RegistryIntrospector output into a validated
        gui_parser_contracts.GuiSchema.
        """
        logger.info(
            "GUI serialization | total_modules=%d | filter=%s",
            len(resolved_objects),
            module_filter or "none",
        )

        id_map: Dict[tuple, str] = {
            (res.module, res.name): str(res.id)
            for attrs in resolved_objects.values()
            for res in attrs.values()
            if res is not None
        }
        logger.debug("Built dependency id_map | entries=%d", len(id_map))

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
                    continue

                if module_filter and resolved.module != module_filter:
                    continue

                if resolved.gui_hidden:
                    hidden.append(self._to_hidden_arg(resolved))
                    total_hidden += 1
                else:
                    spec = self._to_field_spec(
                        resolved,
                        id_map,
                        class_name,
                    )
                    tab_key = spec.tab_label

                    if tab_key not in raw_tabs:
                        raw_tabs[tab_key] = (
                            self._make_tab_meta(resolved.cli.group),
                            [],
                        )

                    raw_tabs[tab_key][1].append(spec)
                    by_module.setdefault(spec.module, []).append(spec.dest)
                    total_visible += 1

        # _required_ref = next((g.ref for g in CliGroup if g.name == "REQUIRED"), "required")
        # _required_ref = CliGroup.REQUIRED.ref
        cli_group_order = {g.ref: i for i, g in enumerate(CliGroup)}
        module_position = {name: i for i, name in enumerate(module_order or [])}

        # def _tab_sort_key(tab_key: str) -> tuple:
        #     # if tab_key == _required_ref:
        #     #     return (0, 0, tab_key)
        #     if tab_key == UNGROUPED_TAB_KEY:
        #         return (3, 0, tab_key)
        #     if tab_key in module_position:
        #         return (1, module_position[tab_key], tab_key)
        #     return (2, cli_group_order.get(tab_key, 999), tab_key)
        #
        # final_tabs: Dict[str, GuiTab] = {
        #     tab_key: GuiTab(tab_meta=tab_meta, args=args)
        #     for tab_key, (tab_meta, args) in sorted(
        #         raw_tabs.items(), key=lambda item: _tab_sort_key(item[0])
        #     )
        # }

        def _tab_sort_key(tab_key: str, tab_data: tuple) -> tuple:
            _, specs = tab_data
            has_required = any(spec.required for spec in specs)
            if has_required:
                return (0, module_position.get(tab_key, 0), tab_key)
            if tab_key == UNGROUPED_TAB_KEY:
                return (3, 0, tab_key)
            if tab_key in module_position:
                return (1, module_position[tab_key], tab_key)
            return (2, cli_group_order.get(tab_key, 999), tab_key)

        final_tabs: Dict[str, GuiTab] = {
            tab_key: GuiTab(tab_meta=tab_meta, args=args)
            for tab_key, (tab_meta, args) in sorted(
                raw_tabs.items(), key=lambda item: _tab_sort_key(item[0], item[1])
            )
        }

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

    ###################################################################################
    # PRIVATE HELPERS
    ###################################################################################

    @staticmethod
    def _normalize_default(value: Any) -> Any:
        """
        Cast pathlib.Path-like default values to str for JSON round-trip safety.
        """
        if value == "None":
            return None
        return str(value) if hasattr(value, "__fspath__") else value

    @staticmethod
    def _normalize_choice(value: Any) -> Any:
        """
        Preserve JSON-safe primitive choice values as-is. Cast everything else to str.
        """
        return value if isinstance(value, _JSON_PRIMITIVES) else str(value)

    @staticmethod
    def _serialize_meta(meta: Any) -> GuiMeta:
        """
        Forward the registry _meta block into a gui_parser_contracts.GuiMeta model.
        """
        return GuiMeta(
            title=getattr(meta, "title", None),
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
        Extract GuiWidgetSpecifics from a miracl.system.datamodels.ResolvedMiraclObj
        and repack it into a gui_parser_contracts.GuiWidgetProps model.
        """
        widget_specifics = resolved.gui.base.props

        if widget_specifics is None:
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
        Construct a gui_parser_contracts.GuiTabMeta from a
        miracl.system.enums.enums_base_modules.CliGroup enum member.
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
        Convert an INTERNAL miracl.system.datamodels.ResolvedMiraclObj (gui_hidden=True)
        into a gui_parser_contracts.GuiHiddenArg.
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
        Resolve a list of sibling argument name strings to UUID strings using the
        pre-built id_map.
        """
        if not names:
            return None

        resolved_uuids: List[str] = []
        for name in names:
            uuid = id_map.get((module, name))
            if uuid is None:
                raise GuiSerializationError(
                    f"'{owner_name}' (module='{module}') has {field}=['{name}'] but no argument named '{name}' exists in module '{module}'. Check for typos in the registry config."
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
        Internal helper to create a structured diagnostic dashboard for GUI-related
        errors.
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

    @staticmethod
    def _resolve_help_text(help_text: Optional[str], default: Any) -> Optional[str]:
        """
        Substitute argparse-style %(default)s placeholders with the actual default
        value so GUI tooltips show the real value rather than the raw format string.
        """
        if not help_text:
            return help_text
        if "%(default)s" not in help_text:
            return help_text
        try:
            return help_text % {"default": default}
        except (KeyError, TypeError, ValueError):
            return help_text

    @classmethod
    def _to_field_spec(
        cls,
        resolved: Any,
        id_map: Dict[tuple, str],
        class_name: str,
    ) -> GuiFieldSpec:
        """
        Convert a visible miracl.system.datamodels.ResolvedMiraclObj (gui_hidden=False)
        into a fully populated gui_parser_contracts.GuiFieldSpec.
        """
        logger.debug(
            "Serializing visible argument | id=%s | name=%s",
            resolved.id,
            resolved.name,
        )

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
            "Tab routing | name=%s | gui.base.group=%s | cli.group.ref=%s",
            resolved.name,
            resolved.gui.base.group if resolved.gui else None,
            resolved.cli.group.ref if resolved.cli.group else None,
            # resolved.cli.group.label if resolved.cli.group else None,
        )

        if resolved.gui and resolved.gui.base.group:
            tab_key = resolved.gui.base.group.ref
            tab_group = resolved.cli.group
            # tab_label = resolved.gui.base.group.label

        elif resolved.cli.group is not None:
            tab_key = resolved.cli.group.ref
            tab_group = resolved.cli.group
            # tab_label = resolved.cli.group.label

        else:
            tab_label = UNGROUPED_TAB_KEY
            tab_group = None
        value_type = (
            resolved.cli.obj_type.python_type
            if resolved.cli.obj_type is not None
            else None
        )

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
                tab_label=tab_key,
                label=gui_base.label,
                # help_text=resolved.cli.help,
                help_text=cls._resolve_help_text(
                    resolved.cli.help,
                    resolved.cli.default,
                ),
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
