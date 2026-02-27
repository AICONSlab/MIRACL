from __future__ import annotations

from typing import Any, Callable, List

from argparse import Namespace
from pydantic import BaseModel


class CommandPlan(BaseModel):
    """
    Execution plan for subprocess/CLI-based module calls.
    Produced by CLICommandBuilder.
    """

    module_name: str
    instance_name: str
    tokens: List[str]
    runner: Callable
    execute: bool

    class Config:
        arbitrary_types_allowed = True  # Required for Callable


class PythonPlan(BaseModel):
    """
    Execution plan for direct Python function calls.
    Produced by PythonNamespaceBuilder.
    """

    module_name: str
    instance_name: str
    runner: Callable
    args: Any  # argparse.Namespace or Pydantic model
    execute: bool

    class Config:
        arbitrary_types_allowed = True  # Required for Callable and Namespace
