"""
Executor Serializer - Creates execution plans with data flow resolution

REFACTOR NOTE: Simple data flow resolution using existing introspector data.
No extra coupling - uses your proof of concept approach.
"""

import shlex
import warnings
from typing import Dict, Any, List
from miracl.system.registry.registry_refactor.datamodels import (
    CommandPlan,
    ExecutionContext,
)


def _flatten_list(values: List[Any]) -> List[str]:
    """
    Recursively flattens nested iterables and converts all values to strings.

    Args:
        values: An iterable that may contain nested lists, tuples, or scalar values.

    Returns:
        A flat list of string representations of all values.

    Examples:
        >>> _flatten_list([1, [2, 3], [[4]], 5])
        ['1', '2', '3', '4', '5']
    """
    flat = []
    for v in values:
        if isinstance(v, (list, tuple)):
            flat.extend(_flatten_list(v))
        else:
            if isinstance(v, str) and v.startswith("[") and v.endswith("]"):
                warnings.warn(
                    f"\n[MIRACL WARNING]: Potential Logic Error.\n "
                    f"The value '{v}' looks like a stringified Python list.\n "
                    f"This usually means a list was passed to a validator that called str() "
                    f"on the whole list instead of the elements.\n",
                    UserWarning,
                )
            flat.append(str(v))
    return flat


class ExecutorSerializer:
    """
    Serializes registry data into CLI command execution plans.

    REFACTOR NOTE: Uses your simple, clean data flow resolution approach.
    No complex helper functions - just straightforward dict operations.
    """

    @staticmethod
    def create_execution_plan(
        parsed_module_objects: Dict[str, Dict[str, Any]],
        parsed_registry_metadata: Dict[str, Dict[str, Any]],
        workflow_config: Any,  # WorkflowConfig - ALWAYS required
    ) -> List[Dict[str, Any]]:
        """
        Creates execution plans with workflow data flow resolution.

        REFACTOR NOTE: workflow_config is ALWAYS required.
        Data flow resolution uses your proof of concept approach.

        Args:
            parsed_module_objects: From introspector.get_modules_as_dict()
                                   {class_name: {variable_name: resolved_dict}}
            parsed_registry_metadata: From introspector.get_registry_metadata_as_dict()
                                     {module_name: registry_entry}
            workflow_config: WorkflowConfig object (REQUIRED)

        Returns:
            List[Dict]: Execution plans ready for MiraclExecutor
        """
        plans: List[Dict[str, Any]] = []

        # REFACTOR: Apply data flow BEFORE building execution plans
        # This is your simple, clean approach from the proof of concept!
        if workflow_config.data_flow:
            for module_instance in workflow_config.execution_order:
                if module_instance in workflow_config.data_flow:
                    data_flow_config = workflow_config.data_flow[module_instance]

                    if not data_flow_config:  # Empty dict - skip
                        continue

                    # For each override: variable_name → reference
                    for variable_name_target, reference in data_flow_config.items():
                        # Parse reference: "conv.output_folder" → ("conv", "output_folder")
                        instance_name_source, variable_name_source = reference.split(
                            ".", 1
                        )

                        # Get class names from workflow config
                        module_type_target = workflow_config.modules[
                            module_instance
                        ].type
                        module_type_source = workflow_config.modules[
                            instance_name_source
                        ].type

                        class_name_target = parsed_registry_metadata[
                            module_type_target
                        ]["obj_class"].__name__
                        class_name_source = parsed_registry_metadata[
                            module_type_source
                        ]["obj_class"].__name__

                        # REFACTOR: Simple override - just copy content!
                        parsed_module_objects[class_name_target][variable_name_target][
                            "content"
                        ] = parsed_module_objects[class_name_source][
                            variable_name_source
                        ]["content"]

        # Build instance → module_type mapping
        execution_order = workflow_config.execution_order
        instance_to_module_type = {
            instance: config.type
            for instance, config in workflow_config.modules.items()
        }

        # Build execution plans
        for instance_name in execution_order:
            module_type = instance_to_module_type[instance_name]

            # Get registry metadata
            if module_type not in parsed_registry_metadata:
                raise ValueError(f"Module type '{module_type}' not found in registry")

            registry_item = parsed_registry_metadata[module_type]
            class_name = registry_item["obj_class"].__name__

            # Get module objects
            if class_name not in parsed_module_objects:
                raise ValueError(f"Class '{class_name}' not found in parsed objects")

            module_item = parsed_module_objects[class_name]

            # Build command tokens
            tokens = shlex.split(registry_item["script"])

            for variable_name, obj_dict in module_item.items():
                flag = f"--{obj_dict['cli_l_flag']}"

                # Apply flag map
                if flag in registry_item["flag_map"]:
                    flag = registry_item["flag_map"][flag]

                tokens.append(flag)
                tokens.append(obj_dict["content"])

            # Flatten tokens
            tokens = _flatten_list(tokens)

            # Create execution plan
            plan = {
                "module_name": instance_name,
                "module_type": module_type,
                "tokens": tokens,
                "runner": registry_item["runner"],
                "execute": registry_item["execute"],
            }

            plans.append(plan)

        return plans
