from typing_extensions import override
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ModuleInstanceConfig(BaseModel):
    """
    Single module instance in a workflow.
    """

    type: str
    params: Dict[str, object] = Field(default_factory=dict)


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
        description="Dict of instance_name -> ModuleInstanceConfig: Mapping of module instance names to their configurations. Keys are instance aliases used in execution_order (e.g., 'conv', 'reg'). Values contain module type and optional parameters/hooks.",
    )
    execution_order: List[str] = Field(
        description="The order in which the modules are executed in the workflow",
    )
    data_flow: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Connections between modules. Format: {'target_instance': {'target_variable': 'DSL expression string'}}. Important: the reference here is to the object name, NOT the name attribute of the object!",
    )
    # Dedicated namespace for variable construction in workflow configs
    vars: Dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow-level variables available to all data_flow expressions via ref:vars.<name>. Vars are evaluated after module defaults are populated but before data_flow, so they can reference CLI-provided module values. See ordering note in WorkflowResolver.resolve().",
        examples=[
            "vars: {base_dir: 'ref:conv.base_dir', out_path: 'pattern:{ref:conv.base_dir}/output'}",
        ],
    )

    class Config:
        extra = "forbid"

    @override
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"WorkflowConfig("
            f"name='{self.name}', "
            f"modules={len(self.execution_order)}, "
            f"connections={sum(len(v) for v in self.data_flow.values())}, "
            f"dataflow='{self.data_flow}', "
            f"vars={len(self.vars)}"
            f")"
        )
