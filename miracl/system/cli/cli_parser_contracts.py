"""
Data transfer objects defining the contracts (data structures) between MIRACL CLI
components i.e. serializer and builder layers. The components are intentionally
coupled but there is no directional coupling since neither owns these contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from miracl.system.enums.enums_base_modules import CliGroup


@dataclass
class SerializedCLI:
    """
    Data transfer object passed from MiraclObjSerializer to MiraclCLIBuilder.

    Produced by: MiraclObjSerializer.serialize_for_cli()
    Consumed by: MiraclCLIBuilder.build_parser()

    Fields:
        args:
            List of serialized argument tuples ready for argparse attachment.
            Each tuple contains:
              - flags   : List[str]         e.g. ["-i", "--in_nii"]
              - kwargs  : Dict[str, Any]    e.g. {"help": "...", "required": True}
              - group   : Optional[CliGroup] e.g. CliGroup.REQUIRED

        meta:
            Opaque command metadata originating from the YAML _meta block.
            Typed as Any — this contract layer has no dependency on MetaConfig
            or any registry/schema concerns. The builder reads from it directly
            via attribute access. Guaranteed to be populated by the loader.
    """

    args: List[Tuple[List[str], Dict[str, Any], Optional[CliGroup]]]
    meta: Any
