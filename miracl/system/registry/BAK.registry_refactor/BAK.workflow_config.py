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

    Simple representation of a workflow YAML with no validation logic.
    Just defines the structure.

    Attributes:
        name:            Workflow name
        description:     Optional workflow description
        version:         Workflow version
        modules:         Dict of instance_name -> ModuleInstanceConfig
        execution_order: List of instance names to execute in order
        data_flow:       Connections between modules
                         Format: {
                             'target_instance': {
                                 'target_variable': 'DSL expression string'
                             }
                         }
        vars:            Workflow-level variables available to all
                         data_flow expressions via ref:vars.<name>.
                         Type widened from Dict[str, str] to Dict[str, Any] so
                         that values can be DSL expressions
                         (e.g. "ref:conv.base_dir") rather than only plain
                         strings. Vars are evaluated after module defaults are
                         populated but before data_flow, so they can reference
                         CLI-provided module values. See ordering note in
                         WorkflowResolver.resolve().
                         Example YAML:
                             vars:
                               base_dir: "ref:conv.base_dir"
                               out_path: "pattern:{ref:conv.base_dir}/output"
                         Example reference in data_flow:
                             output_folder: "ref:vars.out_path"
    """

    name: str
    description: Optional[str] = None
    version: str = "1.0"
    modules: Dict[str, ModuleInstanceConfig]
    execution_order: List[str]
    data_flow: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    # Optional workflow-level variables block.
    # Widened from Dict[str, str] to Dict[str, Any] to support DSL
    # expressions as values. Previously restricted to plain string constants.
    # Values are now parsed and evaluated by WorkflowResolver.resolve() in a
    # dedicated vars resolution step that runs after module defaults
    # are populated but before data_flow, so vars can safely reference
    # CLI-provided values from any module namespace.
    vars: Dict[str, Any] = Field(default_factory=dict)

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
