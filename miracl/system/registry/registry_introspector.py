from typing_extensions import override
from typing import Dict
from miracl.system.registry.registry import MiraclRegistry, RegistryEntry
from miracl.system.registry.schema_validators.config_schema import MetaConfig
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    ResolvedMiraclObj,
)

from miracl.system.logger import get_logger

logger = get_logger(__name__)


class RegistryIntrospector:
    """
    Utility class to introspect a MiraclRegistry and extract all registered
    module objects as structured ResolvedMiraclObj instances.
    """

    def __init__(self, registry: MiraclRegistry) -> None:
        self.registry = registry

        logger.debug(
            "RegistryIntrospector initialised | registry_modules=%d",
            len(self.registry.list_modules()),
        )

    def get_meta(self) -> MetaConfig:
        """
        Return MetaConfig. Same as get_registry_metadata_as_dict() i.e. no processing
        done here. It's just a passthrough to the serializer.

        MetaCOnfig is guaranteed to be present as _load_registry_from_yaml() validates
        the _meta block and calls register_meta() before the registry is even introspected.

        The only way an error is raised here is if the loader was skipped and the
        registry was created manually, which should never be the case!
        """
        return self.registry.get_meta()

    def get_modules_as_dict(self) -> Dict[str, Dict[str, ResolvedMiraclObj]]:
        """
        Resolve all MiraclObj attributes for each registered module in the registry
        and return them as a nested dictionary of structured ResolvedMiraclObj.

        Returns:
            Dict[str, Dict[str, ResolvedMiraclObj]]

        Structure:
        {
            "ModuleClassName": {
                "attribute_name": ResolvedMiraclObj(...)
            }
        }
        """
        logger.info("Resolving registry modules into structured objects")

        resolved_objects: Dict[str, Dict[str, ResolvedMiraclObj]] = {}

        all_modules = self.registry.list_modules()
        logger.debug(
            "Beginning module introspection | total_modules=%d",
            len(all_modules),
        )

        # Track number of resolved args
        total_resolved_args = 0

        for key in all_modules.keys():
            entry = self.registry.get(key)
            module_type = entry["module_type"]
            obj_class = entry["obj_class"]
            class_name = obj_class.__name__

            logger.debug(
                "Introspecting module | registry_key=%s | class=%s | type=%s",
                key,
                class_name,
                module_type.name,
            )

            module_bucket: Dict[str, ResolvedMiraclObj] = {}
            resolved_count = 0

            # Iterate over class attributes to find MiraclObj instances
            for attr_name, attr in vars(obj_class).items():
                if not isinstance(attr, MiraclObj):
                    continue

                resolved = attr.resolve(module_type)

                if resolved is None:
                    logger.debug(
                        "Argument filtered (disabled) | module=%s | attribute=%s",
                        class_name,
                        attr_name,
                    )
                    # DISABLED arguments filtered out here
                    continue

                module_bucket[attr_name] = resolved

                resolved_count += 1
                total_resolved_args += 1
                logger.debug(
                    "Resolved argument | module=%s | attribute=%s",
                    class_name,
                    attr_name,
                )

            resolved_objects[class_name] = module_bucket

            logger.debug(
                "Module introspected | class=%s | resolved_arguments=%d",
                class_name,
                resolved_count,
            )

        logger.success(
            "Registry introspection complete | modules=%d | total_resolved_arguments=%d",
            len(resolved_objects),
            total_resolved_args,
        )

        return resolved_objects

    def get_registry_metadata_as_dict(self) -> Dict[str, RegistryEntry]:
        """
        List all registered modules.

        Returns:
            Dict mapping module names to their full registry entries
        """
        return self.registry.list_modules(verbose=False)

    @override
    def __repr__(self) -> str:
        module_names = ", ".join(self.registry.list_modules().keys())
        module_count = len(self.registry.list_modules())
        return (
            f"<RegistryIntrospector: "
            f"Introspecting {module_count} registered module(s) "
            f"({module_names})>"
        )
