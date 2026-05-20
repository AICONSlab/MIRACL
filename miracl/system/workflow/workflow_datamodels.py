"""
This code is written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Execution plans for modules, currently for subprocess/CLI-based module calls as well
as direct Python function calls.

Use CommandPlan for CLI scripts (via generic_runner).
Use PythonPlan for direct Python function calls.
"""

#######################################################################################
# IMPORTS
#######################################################################################

from __future__ import annotations
from typing import Any, Callable, List, Dict
from pydantic import BaseModel, Field

#######################################################################################
# PLANS
#######################################################################################


class CommandPlan(BaseModel):
    """
    Execution plan for subprocess/CLI-based module calls.

    Produced by CLICommandBuilder.
    """

    module_name: str = Field(
        description="Module type identifier matching the registry",
        examples=["conv_tiff_nii", "reg_clar_allen"],
    )
    instance_name: str = Field(
        description="Alias for this instance that is unique to the workflow. Used in execution_order and data_flow to reference this specific module instance. This is super useful as it allows us to re-use a module instance multiple times with e.g. different input overrides.",
        examples=["conv", "reg", "norm_vox"],
    )
    tokens: List[str] = Field(
        description="CLI flags and args to execute",
        examples=[["--input", "/data/tiffs", "--output", "/data/nii"]],
    )
    runner: Callable = Field(
        description="Callable/executable fn",
        examples=["<function generic_runner>"],
    )
    execute: bool = Field(
        description="Whether to actually run the plan or just prepare it (dry-run)",
    )
    hooks: Dict[str, List[Callable]] = Field(
        default_factory=dict, description="Pre-baked zero-arg hook callables"
    )

    model_config = {"arbitrary_types_allowed": True}


class PythonPlan(BaseModel):
    """
    Execution plan for direct Python function calls.

    Produced by PythonNamespaceBuilder.
    """

    module_name: str = Field(
        description="Module type identifier matching the registry",
        examples=["conv_tiff_nii", "reg_clar_allen"],
    )
    instance_name: str = Field(
        description="Alias for this instance that is unique to the workflow. Used in execution_order and data_flow to reference this specific module instance. This is super useful as it allows us to re-use a module instance multiple times with e.g. different input overrides.",
        examples=["conv", "reg", "norm_vox"],
    )
    runner: Callable = Field(
        description="Python function to execute",
    )
    args: Any = Field(
        description="Args for the runner (currently: argparse.Namespace or Pydantic model)",
        examples=["namespace(input='/data', output='/out')"],
    )
    execute: bool = Field(
        description="Whether to actually run the plan or just prepare it (dry-run)",
    )
    hooks: Dict[str, List[Callable]] = Field(
        default_factory=dict, description="Pre-baked zero-arg hook callables"
    )

    model_config = {"arbitrary_types_allowed": True}
