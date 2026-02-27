from argparse import Namespace
from typing import Any
from miracl.api.core import MiraclObj
from miracl.api.enums import ModuleType


class ParserUtilFns:
    """
    Utility functions for working with argparse parsing results in conjunction
    with resolved MiraclObj definitions.

    This class provides helpers that bridge MiraclObj metadata (flags, resolution
    logic) with the values stored in an argparse Namespace after parsing.
    """

    @staticmethod
    def resolve_flag_value(namespace_obj: Namespace, obj: MiraclObj) -> Any:
        """
        Retrieve the parsed CLI value for a given MiraclObj from an argparse Namespace.

        This function resolves the MiraclObj in MODULE context, extracts the effective
        long CLI flag name, and uses it to access the corresponding attribute on the
        provided argparse Namespace.

        It allows callers to reference parsed CLI values via MiraclObj instances
        instead of hardcoding flag names, keeping CLI access consistent with the
        object registry and resolution logic.

        Args:
            namespace_obj:
                The argparse Namespace returned by ArgumentParser.parse_args().
            obj:
                The MiraclObj whose resolved CLI flag should be used to access
                the corresponding value in the namespace.

        Returns:
            The value stored in the argparse Namespace for the resolved CLI flag.
            The return type depends on the argument configuration (e.g. str, list,
            int, Path).

        Raises:
            KeyError:
                If the resolved object does not define a 'cli_l_flag'.
            AttributeError:
                If the resolved CLI flag is not present on the Namespace.
            ValueError:
                If the object cannot be resolved in MODULE context.
        """
        resolved = obj.resolve(ModuleType.MODULE)
        return getattr(namespace_obj, resolved["cli_l_flag"])
