"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Runner plan type registry and configuration.

Maps runner functions to their ExecutionPlan types and provides builders for generating
execution plans.

Adding a new runner:
    1. Implement the runner under runners/.
    2. Implement the builder under command_builders/ if needed.
    3. Add an entry to RUNNER_PLAN_TYPE_MAP here.
    4. If the runner uses a new plan type, add it to ExecutionPlan above.
"""

# =====================================================================================
# IMPORTS
# =====================================================================================

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple, Type, Union
from miracl.system.workflow.workflow_datamodels import CommandPlan, PythonPlan
from miracl.system.workflow.command_builders.base_builder import ExecutionPlanBuilder
from miracl.system.workflow.command_builders.cli_cmd_builder import CLICommandBuilder
from miracl.system.workflow.runners.generic_runner import generic_runner

# =====================================================================================
# ExecutionPlan type alias
# =====================================================================================
# Manual union to avoid reordering the file. New plan types get added here and its
# respective runner entry gets added to RUNNER_PLAN_TYPE_MAP below. Both changes stay
# in this file.
# =====================================================================================
ExecutionPlan = Union[CommandPlan, PythonPlan]


# =====================================================================================
# Custom exceptions
# =====================================================================================
# Domain-specific exceptions make it straightforward for callers to catch runner
# misconfiguration errors without accidentally processing unrelated built-in
# exceptions. Both inherit from WorkflowConfigurationError so callers can catch either
# specifically or the base class for both.
# =====================================================================================
class WorkflowConfigurationError(Exception):
    """
    Base class for workflow runner map misconfiguration errors.

    Catch this to handle any runner map problem in a single except clause.
    """

    pass


class UnregisteredRunnerError(WorkflowConfigurationError):
    """
    Raised when a runner function is not found in RUNNER_PLAN_TYPE_MAP.

    The error message includes the runner name and the file to edit so a dev knows
    exactly what to add and where.
    """

    pass


# ===========================================================================
# RUNNERS
# ===========================================================================

# ---------------------------------------------------------------------------
# RunnerConfig dataclass
# ---------------------------------------------------------------------------
# Previously I used RunnerEntry = Tuple[Type[ExecutionPlan], Callable, Any] and
# unpacked positionally as plan_type, get_payload, builder = entry.
#
# However, this was not very precise which is why I'm now using named attribute access
# via runner_config.plan_type etc. The builder field is typed against
# ExecutionPlanBuilder rather than Any so that type checkers can verify the contract
# at the map definition # site.
#
# builder_class stores the class rather than an instance. The orchestrator instantiates
# it fresh per plan, which avoids any shared mutable state across plans, runs, and
# threads regardless of whether the builder is currently stateless. However, this is
# only a safety guarantee if the builders are guaranteed stateless!
# ---------------------------------------------------------------------------


@dataclass
class RunnerConfig:
    """
    Configuration for a workflow runner.

    Attributes:
        plan_type: The ExecutionPlan subclass this runner expects.
        get_payload: Callable that extracts positional arguments from a plan.
        builder_class: The builder class that produces this plan type.
    """

    plan_type: Type[ExecutionPlan]
    get_payload: Callable[[Any], Tuple]
    builder_class: Type[ExecutionPlanBuilder]


# ---------------------------------------------------------------------------
# Runner contract registry
# ---------------------------------------------------------------------------
# Each entry maps a runner function to a RunnerConfig describing:
#     plan_type:     The plan class this runner expects.
#     get_payload:   Extracts the runner's positional arguments from a plan.
#     builder_class: The builder class that produces this plan type.
#                    Instantiated fresh per plan in the orchestrator.
#
# Adding a new runner:
#     1. Implement the runner under runners/.
#     2. Implement the builder under command_builders/ if needed.
#     3. Add an entry here. No other files need to change.
#     4. If the runner uses a new plan type, add it to ExecutionPlan above.
# ---------------------------------------------------------------------------

RUNNER_PLAN_TYPE_MAP: Dict[Callable, RunnerConfig] = {
    generic_runner: RunnerConfig(
        plan_type=CommandPlan,
        get_payload=lambda plan: (plan.tokens, plan.execute),
        builder_class=CLICommandBuilder,
    ),
    # TODO: I will have to implement this later. For now I only have CLI runners but I
    # leave it here for now. Once this will be used I must not forget to import the
    # PythonNamespaceBuilder that already exists!
    # python_runner: RunnerConfig(
    #     plan_type=PythonPlan,
    #     get_payload=lambda plan: (plan.args, plan.execute),
    #     builder_class=PythonNamespaceBuilder,
    # ),
}
