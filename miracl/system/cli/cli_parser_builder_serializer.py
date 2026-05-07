"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Serializer takes output from the registry introspector and converts it into the format
expected by the CLI parser builder.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import ResolvedMiraclObj
from miracl.system.cli.cli_parser_contracts import SerializedCLI
from miracl.system.datamodels.miraclobj_datamodel import MIRACL_HIDE_HELP
from argparse import SUPPRESS
from miracl.system.logger import get_logger

logger = get_logger(__name__)


class MiraclObjSerializer:
    """
    Converts resolved objects from the RegistryIntrospector into the format expected
    by the CLI argparse builder.
    """

    @classmethod
    def _format_metavar(
        cls,
        name: str,
        metavar: Union[str, Tuple[str, ...], List[str], None],
    ) -> str:
        """
        Always returns a single, uppercased string. Handles both single strings and
        sequences (tuples/lists). This is more or less cosmetic but we want the meta
        field in the parser help to be uppercase by convention.
        """
        source = metavar if metavar is not None else name

        if isinstance(source, (list, tuple)):
            return ", ".join(str(s).upper() for s in source)

        return str(source).upper()

    @classmethod
    def _to_argparse_format(
        cls,
        resolved: ResolvedMiraclObj,
        module_parser: bool,
    ) -> Tuple[List[str], Dict[str, Any], Optional[CliGroup]]:
        """
        Convert a single ResolvedMiraclObj into (flags, kwargs, group) for argparse.
        This is an important function as it defines how the argparser objects are built
        from the introspector output.
        """
        logger.debug(
            "Serializing argument for CLI | id=%s | name=%s | module_parser=%s",
            resolved.id,
            resolved.name,
            module_parser,
        )

        flags: List[str] = []

        if resolved.cli.s_flag:
            flags.append(f"-{resolved.cli.s_flag}")

        flags.append(f"--{resolved.cli.l_flag}")

        help_text = (
            SUPPRESS if resolved.cli.help == MIRACL_HIDE_HELP else resolved.cli.help
        )

        kwargs: Dict[str, Any] = {
            "help": help_text,
            "dest": str(resolved.cli.l_flag) if module_parser else str(resolved.id),
            "metavar": cls._format_metavar(
                name=resolved.name,
                metavar=resolved.cli.metavar,
            ),
            "required": resolved.cli.required
            if resolved.cli.required is not None
            else False,
        }

        if resolved.cli.obj_type:
            kwargs["type"] = resolved.cli.obj_type.cli_parser

        if resolved.cli.default is not None:
            kwargs["default"] = resolved.cli.default

        if resolved.cli.nargs is not None:
            kwargs["nargs"] = resolved.cli.nargs

        if resolved.cli.choices is not None:
            kwargs["choices"] = resolved.cli.choices

        if resolved.cli.action:
            kwargs["action"] = resolved.cli.action.value

        if resolved.cli.const is not None:
            kwargs["const"] = resolved.cli.const

        logger.debug(
            "Serialized argument | flags=%s | dest=%s",
            flags,
            kwargs.get("dest"),
        )

        return flags, kwargs, resolved.cli.group

    @classmethod
    def serialize_for_cli(
        cls,
        resolved_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        meta: Any,
        module_parser: bool = False,
    ) -> SerializedCLI:
        """
        Flatten the nested introspector dict into a list of CLI-ready entries. The
        list is then used with the above, internal `_to_argparse_format` function that
        actually converts the objects to argparser format.

        Returns:
            List of tuples: (flags, kwargs, cli_group)
        """
        logger.info(
            "Serializing resolved objects for CLI | module_parser=%s",
            module_parser,
        )

        serialized: List[Tuple[List[str], Dict[str, Any], Optional[CliGroup]]] = []

        total_modules = len(resolved_objects)
        total_arguments = 0

        logger.debug(
            "Beginning CLI serialization | total_modules=%d",
            total_modules,
        )

        for module_name, attrs in resolved_objects.items():
            logger.debug(
                "Serializing module arguments | module_class=%s | arg_count=%d",
                module_name,
                len(attrs),
            )
            for resolved in attrs.values():
                if resolved is None:
                    continue  # NOTE: Skip filtered/disabled args

                # NOTE: Returned tuple that matches argparse requirements
                serialized.append(cls._to_argparse_format(resolved, module_parser))
                total_arguments += 1

        logger.success(
            "CLI serialization complete | modules=%d | total_arguments=%d",
            total_modules,
            total_arguments,
        )

        return SerializedCLI(args=serialized, meta=meta)
