"""
gui_serializer.py
=================

Converts ``ResolvedMiraclObj`` instances from ``RegistryIntrospector`` into
a ``GuiSchema`` — a Pydantic model that drives the GUI builder.

Responsibility
--------------
Produce a ``GuiSchema`` containing one ``GuiFieldSpec`` per argument.
Each ``GuiFieldSpec.id`` is ``str(uuid)`` — the key the deserializer expects.

That's it. The GUI builder reads the schema. The widget factory creates
widgets from individual specs. When the user clicks Run, the builder calls
``on_run({str(uuid): value, ...})``. That dict is the sole output of the
GUI layer and the direct input to ``deserialize_parsed_args_to_objects``.

Adding a new frontend
---------------------
Subclass ``BaseGuiSerializer``, pass ``frontend="yourname"`` to super, and
override ``_post_process`` if you need to filter or enrich specs::

    class GradioGuiSerializer(BaseGuiSerializer):
        def __init__(self):
            super().__init__(frontend="gradio")
"""

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
    ResolvedMiraclObj,
    ArgumentType,
    WidgetType,
    RangeFormConfig,
    LineEditConfig,
    GuiChoiceOverrideConfig,
)
from miracl.system.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# EXCEPTION
# ─────────────────────────────────────────────────────────────────────────────


class GuiSerializationError(ValueError):
    """Raised when a ``ResolvedMiraclObj`` is missing required GUI metadata."""


# ─────────────────────────────────────────────────────────────────────────────
# FIELD SPEC
# ─────────────────────────────────────────────────────────────────────────────


class GuiFieldSpec(BaseModel):
    """
    Everything the widget factory needs to build one widget.

    ``id`` is ``str(uuid)`` — this becomes the key in the dict passed to
    ``deserialize_parsed_args_to_objects``, mirroring ``dest=str(resolved.id)``
    in the CLI serializer.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: str  # str(UUID) — the deserializer key
    name: str
    label: str
    help: str
    widget_type: WidgetType  # required — never inferred
    obj_type: Optional[ArgumentType]
    default: Optional[Any]
    required: bool
    choices: Optional[List[Any]]
    choice_labels: Optional[List[Any]]
    group: Optional[str]
    order: Optional[float]
    hidden: bool  # INTERNAL args: in payload, not shown
    range_config: Optional[RangeFormConfig]
    text_config: Optional[LineEditConfig]
    extensions: Dict[str, Any]  # gui.extensions[frontend] slice
    module: str
    module_group: str
    deprecated: bool


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA  — the save/load unit handed to the builder
# ─────────────────────────────────────────────────────────────────────────────


class GuiSchema(BaseModel):
    """
    Top-level GUI definition.

    ``fields``    — flat ordered list; the builder iterates this.
    ``groups``    — ordered unique tab names (from visible fields).
    ``by_module`` — module → [field ids]; for filtering and future REST use.

    JSON round-trip::

        json_str = schema.model_dump_json(indent=2)
        schema   = GuiSchema.model_validate_json(json_str)
    """

    model_config = ConfigDict(frozen=True)

    frontend: str
    fields: List[GuiFieldSpec]
    groups: List[str]
    by_module: Dict[str, List[str]]

    @model_validator(mode="after")
    def _validate_consistency(self) -> "GuiSchema":
        declared = set(self.groups)
        from_fields = {f.group or "General" for f in self.fields if not f.hidden}
        missing = from_fields - declared
        if missing:
            raise ValueError(f"GuiSchema.groups missing entries: {missing}")

        field_ids = {f.id for f in self.fields}
        for module, ids in self.by_module.items():
            unknown = set(ids) - field_ids
            if unknown:
                raise ValueError(
                    f"by_module['{module}'] references unknown field IDs: {unknown}"
                )
        return self

    def fields_for_group(self, group: str) -> List[GuiFieldSpec]:
        return [
            f for f in self.fields if not f.hidden and (f.group or "General") == group
        ]

    def fields_for_module(self, module: str) -> List[GuiFieldSpec]:
        ids = set(self.by_module.get(module, []))
        return [f for f in self.fields if f.id in ids]


# ─────────────────────────────────────────────────────────────────────────────
# BASE SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────


class BaseGuiSerializer(abc.ABC):
    def __init__(self, frontend: str) -> None:
        self._frontend = frontend

    def serialize(
        self,
        resolved_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        module_filter: Optional[str] = None,
    ) -> GuiSchema:
        """
        Convert ``RegistryIntrospector.get_modules_as_dict()`` output into a
        ``GuiSchema``.

        Parameters
        ----------
        resolved_objects
            ``{ClassName: {attr_name: ResolvedMiraclObj}}``
        module_filter
            When set, include only fields whose ``module`` matches.

        Raises
        ------
        GuiSerializationError
            If any argument is missing ``gui`` or ``widget_type``.
        """
        logger.info(
            "GUI serialization | frontend=%s | filter=%s",
            self._frontend,
            module_filter or "none",
        )

        specs: List[GuiFieldSpec] = []

        for class_name, attrs in resolved_objects.items():
            for attr_name, resolved in attrs.items():
                if resolved is None:
                    continue
                if module_filter and resolved.module != module_filter:
                    continue
                specs.append(self._to_field_spec(resolved, self._frontend))

        specs.sort(key=lambda s: (s.group or "\xff", s.order or 0.0))
        specs = self._post_process(specs)

        # Ordered unique groups from visible fields
        seen: set = set()
        groups: List[str] = []
        for s in specs:
            if s.hidden:
                continue
            key = s.group or "General"
            if key not in seen:
                seen.add(key)
                groups.append(key)

        # module → [field ids]
        by_module: Dict[str, List[str]] = {}
        for s in specs:
            by_module.setdefault(s.module, []).append(s.id)

        schema = GuiSchema(
            frontend=self._frontend,
            fields=specs,
            groups=groups,
            by_module=by_module,
        )
        logger.success(
            "GUI serialization complete | fields=%d | groups=%s",
            len(specs),
            groups,
        )
        return schema

    @staticmethod
    def _to_field_spec(resolved: ResolvedMiraclObj, frontend: str) -> GuiFieldSpec:
        if resolved.gui is None:
            raise GuiSerializationError(
                f"'{resolved.name}' (module='{resolved.module}') has no 'gui' block."
            )

        gui_base = resolved.gui.base

        if gui_base.widget_type is None:
            raise GuiSerializationError(
                f"'{resolved.name}' (module='{resolved.module}', group='{resolved.module_group}') is missing 'widget_type' - widget types must be declared explicitly."
            )

        raw_labels = gui_base.label
        label = " / ".join(raw_labels) if raw_labels else resolved.name

        all_ext = resolved.gui.extensions or {}
        extensions = all_ext.get(frontend, {})

        props = gui_base.props
        range_config = props.range if props else None
        text_config = props.text if props else None
        choices_cfg = props.choices if props else None

        # Cast choices to strings for JSON round-trip safety.
        # Raw choices may be Python Enums, ints, or other objects that lose
        # their type when serialised to JSON and back.  String keys are safe
        # across the boundary; the deserializer handles the cast back via
        # ArgumentType.python_type.  NOTE: if choices are complex objects that
        # cannot be meaningfully stringified, re-evaluate at call site.
        raw_choices = resolved.cli.choices
        choices = [str(c) for c in raw_choices] if raw_choices else None
        choice_labels = (
            choices_cfg.vals if choices and choices_cfg and choices_cfg.vals else None
        )

        # Cast Path-like defaults to str for JSON safety
        default = resolved.cli.default
        if hasattr(default, "__fspath__"):
            default = str(default)

        return GuiFieldSpec(
            id=str(resolved.id),
            name=resolved.name,
            label=label,
            help=resolved.cli.help,
            widget_type=gui_base.widget_type,
            obj_type=resolved.cli.obj_type,
            default=default,
            required=resolved.cli.required or False,
            choices=choices,
            choice_labels=choice_labels,
            group=gui_base.group,
            order=gui_base.order,
            hidden=resolved.gui_hidden,
            range_config=range_config,
            text_config=text_config,
            extensions=extensions,
            module=resolved.module,
            module_group=resolved.module_group,
            deprecated=resolved.deprecated,
        )

    def _post_process(self, specs: List[GuiFieldSpec]) -> List[GuiFieldSpec]:
        return specs


# ─────────────────────────────────────────────────────────────────────────────
# CONCRETE SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────


class PyQtGuiSerializer(BaseGuiSerializer):
    """
    Serializer for the PyQt frontend.

    Reads ``gui.extensions.get("qt", {})`` for Qt-specific overrides
    (``"suffix"``, ``"placeholder"``, ``"height"``).

    Usage::

        serializer = PyQtGuiSerializer()
        schema     = serializer.serialize(introspector.get_modules_as_dict())

        # Per-module filtering
        schema = serializer.serialize(module_objects, module_filter="clar_allen")

        # Save / load (for future save/load feature)
        Path("schema.json").write_text(schema.model_dump_json(indent=2))
        schema = GuiSchema.model_validate_json(Path("schema.json").read_text())
    """

    def __init__(self) -> None:
        super().__init__(frontend="qt")
