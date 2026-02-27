import shlex
import warnings
from typing import Dict, Any, Iterable, List
from miracl.system.registry.registry_refactor.datamodels import (
    CommandPlan,
    ExecutionContext,
)


def _flatten_list(values: Iterable[Any]) -> List[str]:
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
                    f"\n[MIRACL WARNING]: Potential Logic Error.\n The value '{v}' looks like a stringified Python list.\n This usually means a list was passed to a validator that called str() on the whole list instead of the elements.\n",
                    UserWarning,
                )
            flat.append(str(v))
    return flat


class SerializerExecutor:
    """
    Serializes validated registry data into CLI command execution plans.

    Transforms registry metadata and module objects into CommandPlan objects
    ready for execution by RegistryExecutor.
    """

    @staticmethod
    def create_execution_plan(
        parsed_module_objects: Dict[str, Any],
        parsed_registry_metadata: ExecutionContext,
        workflow_config: Any,
    ) -> List[CommandPlan]:
        """
        Creates a list of CommandPlan objects from registry metadata and module objects.

        For each registered module, this method:
        1. Extracts the script path from registry metadata
        2. Retrieves module objects by class name
        3. Builds flag-value pairs from module configuration
        4. Applies flag overrides from the registry's flag_map
        5. Flattens all nested values into string tokens
        6. Creates a CommandPlan with tokens, runner, and execute flag

        Args:
            parsed_module_objects: Dictionary mapping class names to their configuration
                containers. Each container has 'cli_l_flag' and 'content' keys.
                Example: {'ConvTiffNiiObjs': {'mctn_folder': {...}, ...}}
            parsed_registry_metadata: Dictionary mapping registry keys to registry entries
                containing 'obj_class', 'script', 'runner', 'flag_map', and 'execute'.
                Example: {'conversion': {'script': 'python ...', 'runner': ..., ...}}

        Returns:
            List[CommandPlan]: List of CommandPlan objects, one per registered module.
            Each CommandPlan contains:
                - module_name: Registry key (e.g., 'conversion', 'registration')
                - tokens: Flattened list of CLI tokens ready for subprocess execution
                - runner: Wrapped runner function from registry
                - execute: Boolean flag indicating whether to actually run the command

        Examples:
            >>> introspector = RegistryIntrospector(registry)
            >>> modules = introspector.get_modules_as_dict()
            >>> metadata = introspector.get_registry_metadata_as_dict()
            >>> plans = SerializerExecutor.create_execution_plan(modules, metadata)
            >>> plans[0].module_name
            'conversion'
            >>> plans[0].tokens
            ['python', '/code/miracl/conv/...', '--down', '5', '--channum', '0', ...]
            >>> plans[0].execute
            True
        """
        plans: List[CommandPlan] = []

        if workflow_config.data_flow:
            for module_instance in workflow_config.execution_order:
                if module_instance in workflow_config.data_flow:
                    data_flow_config = workflow_config.data_flow[module_instance]

                    if not data_flow_config:
                        continue

                    for variable_name_target, reference in data_flow_config.items():
                        instance_name_source, variable_name_source = reference.split(
                            ".", 1
                        )
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

                        parsed_module_objects[class_name_target][variable_name_target][
                            "content"
                        ] = parsed_module_objects[class_name_source][
                            variable_name_source
                        ]["content"]

        execution_order = workflow_config.execution_order
        instance_to_module_type = {
            instance: config.type
            for instance, config in workflow_config.modules.items()
        }

        for instance_name in execution_order:
            module_type = instance_to_module_type[instance_name]

            if module_type not in parsed_registry_metadata:
                raise ValueError(f"Module type '{module_type}' not found in registry.")

            registry_item = parsed_registry_metadata[module_type]
            class_name = registry_item["obj_class"].__name__

            if class_name not in parsed_module_objects:
                raise ValueError(f"Class '{class_name}' not found in parsed objects.")

            # for registry_key, registry_item in parsed_registry_metadata.items():
            #     class_name = registry_item["obj_class"].__name__

            module_item = parsed_module_objects[class_name]

            tokens = shlex.split(registry_item["script"])

            for ctn in module_item.values():
                flag = f"--{ctn['cli_l_flag']}"
                if flag in registry_item["flag_map"]:
                    flag = registry_item["flag_map"][flag]
                tokens.append(flag)
                tokens.append(ctn["content"])

            tokens = _flatten_list(tokens)

            plan = CommandPlan(
                # module_name=registry_key,
                module_name=instance_name,
                tokens=tokens,
                runner=registry_item["runner"],
                execute=registry_item["execute"],
            )

            plans.append(plan)

        return plans
