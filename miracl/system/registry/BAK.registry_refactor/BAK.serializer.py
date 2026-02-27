from typing import Dict, Any, List, Tuple, Optional, Union, cast
from miracl.system.enums.enums_base_modules import CliGroup

Nargs = Optional[Union[int, str]]
MetavarInput = Optional[Union[str, Tuple[str, ...]]]


class MiraclObjSerializer:
    """
    Converts resolved objects from the RegistryIntrospector into a format
    suitable for building argparse parsers.
    """

    @classmethod
    def _format_metavar(
        cls,
        name: str,
        metavar: Union[str, Tuple[str, ...], List[str], None],
    ) -> str:
        """
        Always returns a single uppercased string.
        Handles both single strings and sequences (tuples/lists).
        """
        source = metavar if metavar is not None else name

        if isinstance(source, (list, tuple)):
            return ", ".join(str(s).upper() for s in source)

        return str(source).upper()

    @classmethod
    def _to_argparse_format(
        cls,
        resolved: Dict[str, Any],
        module_parser: bool,
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Convert a single resolved object dictionary into (flags, kwargs) for argparse.

        Args:
            resolved: Dictionary output from MiraclObj.resolve()

        Returns:
            Tuple[List[str], Dict[str, Any]] suitable for parser.add_argument()
        """
        flags: List[str] = []
        if resolved.get("cli_s_flag"):
            flags.append(f"-{resolved['cli_s_flag']}")
        if not resolved.get("cli_l_flag"):
            raise ValueError(
                f"Missing required 'cli_l_flag' in resolved object: {resolved.get('name', 'unknown')}"
            )
        flags.append(f"--{resolved['cli_l_flag']}")

        kwargs: Dict[str, Any] = {
            "help": resolved.get("cli_help", ""),
            "dest": str(resolved["cli_l_flag"])
            if module_parser
            else str(resolved["id"]),
            "metavar": cls._format_metavar(
                name=str(resolved.get("name")),
                metavar=resolved.get("cli_metavar"),
            ),
            "required": resolved.get("cli_required", False),
        }

        if resolved.get("cli_obj_type"):
            kwargs["type"] = resolved["cli_obj_type"].python_type
        if resolved.get("obj_default") is not None:
            kwargs["default"] = resolved["obj_default"]
        if resolved.get("cli_nargs") is not None:
            kwargs["nargs"] = resolved["cli_nargs"]
        if resolved.get("cli_choices") is not None:
            kwargs["choices"] = resolved["cli_choices"]
        if resolved.get("cli_action"):
            kwargs["action"] = resolved["cli_action"].value
        if resolved.get("cli_const") is not None:
            kwargs["const"] = resolved["cli_const"]

        # Include optional grouping info
        cli_group: Optional[CliGroup] = resolved.get("cli_group")
        return flags, kwargs, cli_group

    @classmethod
    def serialize_for_cli(
        cls,
        resolved_objects: Dict[str, Dict[str, Any]],
        module_parser: bool = False,
    ) -> List[Tuple[List[str], Dict[str, Any], Optional[CliGroup]]]:
        """
        Flatten the nested introspector dict into a list of CLI-ready entries.

        Returns:
            List of tuples: (flags, kwargs, cli_group)
        """
        serialized: List[Tuple[List[str], Dict[str, Any], Optional[CliGroup]]] = []
        for attrs in resolved_objects.values():
            for resolved in attrs.values():
                if resolved is None:
                    raise ValueError(
                        "serialize_for_cli encountered a None object at serialization stage. This should have been filtered out by the resolver."
                    )
                flags, kwargs, cli_group = cls._to_argparse_format(
                    resolved, module_parser
                )
                serialized.append((flags, kwargs, cli_group))
        return serialized
