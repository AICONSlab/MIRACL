from typing import Dict, Any, Union
from argparse import Namespace

# from miracl.system.datamodels.datamodel_miracl_objs_refactored import ResolvedMiraclObj
from miracl.system.datamodels.miraclobj_datamodel import ResolvedMiraclObj
from miracl.system.logger import get_logger

logger = get_logger(__name__)  # >>> ADDED: Logger for deserialization


def deserialize_parsed_args_to_objects(
    parsed_args: Union[Namespace, Dict[str, Any]],
    resolved_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
    strict: bool = True,
) -> Dict[str, Dict[str, ResolvedMiraclObj]]:
    """
    Assign parsed CLI arguments to ResolvedMiraclObj.content by matching UUIDs.

    Args:
        parsed_args: Parsed CLI arguments from argparse (keys are UUID strings)
        resolved_objects: The nested dictionary output from Introspector.get_modules_as_dict()
        strict: If True, raise error for unmatched UUIDs; if False, skip silently

    Returns:
        A new nested dictionary with populated 'content' fields.

    Raises:
        ValueError: If strict=True and a UUID in parsed_args doesn't match any object
    """
    if isinstance(parsed_args, Namespace):
        parsed_args = vars(parsed_args)

    logger.info("Deserializing parsed CLI arguments | total_args=%d", len(parsed_args))

    # 1. Build a flat lookup dictionary for O(1) UUID matching
    # Maps UUID string -> (ModuleClassName, AttributeName, ResolvedMiraclObj)
    uuid_lookup = {}
    for class_name, attrs in resolved_objects.items():
        for attr_name, obj in attrs.items():
            uuid_lookup[str(obj.id)] = (class_name, attr_name, obj)

    logger.debug("Built UUID lookup table | total_objects=%d", len(uuid_lookup))

    # 2. Prepare the output nested dictionary (shallow copy of structure)
    populated_objects: Dict[str, Dict[str, ResolvedMiraclObj]] = {
        cls_name: {attr_name: obj for attr_name, obj in attrs.items()}
        for cls_name, attrs in resolved_objects.items()
    }

    updated_count = 0
    unmatched_uuids = []

    # 3. Process each parsed argument
    for uuid_str, value in parsed_args.items():
        # Look up object
        if uuid_str not in uuid_lookup:
            if strict:
                logger.error("UUID not found in lookup | uuid=%s", uuid_str)
                raise ValueError(
                    f"No ResolvedMiraclObj found for UUID '{uuid_str}'. "
                    f"This indicates a mismatch between serializer and deserializer."
                )

            logger.warning(
                "Skipping unknown UUID in non-strict mode | uuid=%s", uuid_str
            )
            continue

        class_name, attr_name, obj = uuid_lookup[uuid_str]

        # 4. Safely update the frozen object
        # We use .model_copy(update=...) because the object is frozen=True.
        # This creates a new instance with the 'content' field populated.
        updated_obj = obj.model_copy(update={"content": value})

        # 5. Store the populated object in our output dictionary
        populated_objects[class_name][attr_name] = updated_obj

        updated_count += 1
        logger.debug(
            "Updated ResolvedMiraclObj | class=%s | attr=%s | value=%s",
            class_name,
            attr_name,
            value,
        )

    logger.info(
        "Deserialization complete | updated_objects=%d | unmatched_uuids=%d",
        updated_count,
        len(unmatched_uuids),
    )

    return populated_objects
