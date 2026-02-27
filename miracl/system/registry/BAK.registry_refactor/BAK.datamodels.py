from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, Callable, List
from uuid import UUID


class ResolvedObject(BaseModel):
    id: UUID
    content: Any = None


class ArgMetadata(BaseModel):
    cli_l_flag: str
    cli_required: bool = False
    gui_hidden: bool = False


class ExecutionContext(BaseModel):
    script: str
    runner: Callable
    arg_metadata: Dict[str, ArgMetadata]
    flag_map: Dict[str, str]


class ModuleDataPackage(BaseModel):
    """Data and Rules for a single module."""

    context: ExecutionContext
    objects: Dict[str, ResolvedObject]


class RegistryState(BaseModel):
    """Snapshot of all n modules in the registry."""

    modules: Dict[str, ModuleDataPackage]


class CommandPlan(BaseModel):
    """The final tokens for one specific module."""

    module_name: str
    instance_name: str
    tokens: List[str]
    runner: Callable
    execute: bool

    class Config:
        arbitrary_types_allowed = True  # Required for Callable and Namespace


class PythonPlan(BaseModel):
    module_name: str
    instance_name: str
    runner: Callable
    args: Any  # argparse.Namespace or Pydantic model
    execute: bool

    class Config:
        arbitrary_types_allowed = True  # Required for Callable and Namespace


class WorkflowPlan(BaseModel):
    """The complete batch of plans to be executed."""

    plans: List[CommandPlan]
