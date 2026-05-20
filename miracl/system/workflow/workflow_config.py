"""
This code is written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Workflow configuration data models. Defines the structure for workflow YAML configs
used by WorkflowResolver to orchestrate module execution.
"""

#######################################################################################
# IMPORTS
#######################################################################################

from typing_extensions import override
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional, Set

#######################################################################################
# CONFIGS
#######################################################################################


class LifecycleHooks(BaseModel):
    """
    Container for lifecycle hook definitions.

    Each hook type contains a list of DSL expression strings that will be evaluated
    and executed at the corresponding point in the workflow lifecycle.

    This feature is generally useful but is also needed as some MIRACL workflows can
    be a bit hacky. Until we can refactor them all we need to be able to run actions
    pre and post modules in the workflow.

    The on_failure and on_success methods are also generally a good addition but can
    also be used in the Graphviz/Dot visualization down the road.

    Example YAML:
        hooks:
          pre_run:
            - "fn:create_ort2std_file(...)"
          post_run:
            - "fn:move_results(...)"
    """

    pre_run: List[str] = Field(default_factory=list)
    post_run: List[str] = Field(default_factory=list)
    on_failure: List[str] = Field(default_factory=list)
    on_success: List[str] = Field(default_factory=list)


class ModuleInstanceConfig(BaseModel):
    """
    Single module instance in a workflow.
    """

    type: str
    params: Dict[str, object] = Field(default_factory=dict)
    hooks: LifecycleHooks = Field(default_factory=LifecycleHooks)


class ModuleDataFlow(BaseModel):
    """
    Explicit input/output data-flow contract for a single module instance.

    The param name on the output side is irrelevant to DAG construction; only the var
    key extracted from the value expression matters. Using the var name as the key is
    recommended for human readability but not enforced.
    """

    input: Dict[str, str] = Field(default_factory=dict)
    output: Dict[str, str] = Field(default_factory=dict)

    @validator("output")
    @classmethod
    def output_values_must_be_var_refs(cls, v: Dict[str, str]) -> Dict[str, str]:
        """
        Enforce that every output value is a ref:vars.<key> expression.

        Raises:
            ValueError: For any output value that does not start with ref:vars.
        """
        for param, expr in v.items():
            if not expr.startswith("ref:vars."):
                raise ValueError(
                    f"output['{param}']: value must be a 'ref:vars.<key>' expression, got '{expr}'. Only refs into the vars namespace are permitted on the output side."
                )
        return v

    class Config:
        extra = "forbid"


class WorkFlowConfig(BaseModel):
    """
    Workflow configuration data model.

    Simple representation of a workflow YAML with no validation logic. Just defines
    the structure.
    """

    name: str = Field(
        description="Workflow name",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional workflow description",
    )
    version: str = Field(
        default="1.0",
        description="Version of this workflow",
    )
    modules: Dict[str, ModuleInstanceConfig] = Field(
        description=(
            "Dict of instance_name -> ModuleInstanceConfig: Mapping of module instance names to their configurations. Keys are instance aliases used in execution_order (e.g., 'conv', 'reg'). Values contain module type and optional parameters/hooks."
        ),
    )
    execution_order: List[str] = Field(
        description="The order in which the modules are executed in the workflow",
    )
    data_flow: Dict[str, ModuleDataFlow] = Field(
        default_factory=dict,
        description=(
            "Per-module input/output data-flow declarations. Format: {'instance_name': {'input': {'param': 'DSL expr'}, 'output': {'label': 'ref:vars.<key>'}}}. The 'output' block is used by WorkflowGraph to derive producer→consumer edges; values must be 'ref:vars.*' expressions. The 'input' block drives both parameter resolution and consumer edges."
        ),
    )
    # NOTE: Dedicated namespace for variable construction in workflow configs
    vars: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Workflow-level variables available to all data_flow expressions via ref:vars.<name>. Vars are evaluated after module defaults are populated but before data_flow, so they can reference CLI-provided module values. See ordering note in WorkflowResolver.resolve()."
        ),
        examples=[
            "vars: {base_dir: 'ref:conv.base_dir', out_path: 'pattern:{ref:conv.base_dir}/output'}",
        ],
    )

    def resolve_tab_order(
        self, known_module_names: Optional[Set[str]] = None
    ) -> List[str]:
        seen: Set[str] = set()
        order: List[str] = []
        for instance_name in self.execution_order:
            module_type = self.modules[instance_name].type
            if module_type in seen:
                continue
            if known_module_names is not None and module_type not in known_module_names:
                continue
            seen.add(module_type)
            order.append(module_type)
        return order

    class Config:
        extra = "forbid"

    @override
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"WorkflowConfig("
            f"name='{self.name}', "
            f"modules={len(self.execution_order)}, "
            f"connections={sum(len(v.input) + len(v.output) for v in self.data_flow.values())}, "
            f"dataflow='{self.data_flow}', "
            f"vars={len(self.vars)}"
            f")"
        )
