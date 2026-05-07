"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Deserializer takes the output (dict) from either a GUI or a CLI parser and deserializes
it back into the objects dictionary. It matches the args and their content with the
respective object and its content attribute through UUID's.

Note:
  Still needs correct docs formatting, headers etc. i.e. should adhere to the dev style
  docs that have been suggested by the team internally.
"""

from typing import Dict, Any, Union
from argparse import Namespace
from uuid import UUID
from miracl.system.datamodels.miraclobj_datamodel import ResolvedMiraclObj
from miracl.system.logger import get_logger

logger = get_logger(__name__)


def _is_uuid(value: str) -> bool:
    """
    Return True if value is a valid UUID string.

    Used to filter argparse injected internal keys (e.g. subparser dest names, _subparser)
    and GUI framework keys from the parsed args dict before UUID lookup. These non-UUID
    keys are intentionally skipped. Only keys produced by the serializer's
    dest=str(resolved.id) pattern should reach the loopup.
    """
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def deserialize_parsed_args_to_objects(
    parsed_args: Union[Namespace, Dict[str, Any]],
    resolved_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
) -> Dict[str, Dict[str, ResolvedMiraclObj]]:
    """
    Assign parsed CLI/GUI arguments to ResolvedMiraclObj.content by matching UUIDs.

    Both the CLI path (argparse Namespace) and the GUI path (PyQt result dict) produce
    UUID-keyed entries via dest=str(resolved.id) in the serializer. Non-UUID keys
    injected by argparse internals or GUI frameworks are silently skipped by the
    _is_uuid filter since they are never MIRACL argument values.

    A UUID key that passes the filter but has no matching object is a pipeline assembly
    error (serializer and deserializer were called with different resolved_objects
    instances) and raises immediately!!! This has not been the case before which could
    potentially have caused silent mismatches between argument and content destination.

    Args:
        parsed_args: Parsed arguments from argparse (Namespace) or a GUI builder
                     (Dict). All (!) MIRACL argument keys are UUID strings!!
        resolved_objects: Output of RegistryIntrospector.get_modules_as_dict().

    Returns:
        A new nested dictionary with populated 'content' fields. The original
        resolved_objects is not modified. Frozen ResolvedMiraclObj instances are
        replaced with model_copy(update={"content": value}) copies.

    Raises:
        RuntimeError: If a UUID key passes the filter but has no matching ResolvedMiraclObj.
                      This will always be a programming error, not a user input error.
    """
    if isinstance(parsed_args, Namespace):
        parsed_args = vars(parsed_args)

    logger.info("Deserializing parsed arguments | total_args=%d", len(parsed_args))

    uuid_lookup: Dict[str, tuple] = {}
    for class_name, attrs in resolved_objects.items():
        for attr_name, obj in attrs.items():
            uuid_lookup[str(obj.id)] = (class_name, attr_name, obj)

    logger.debug("Built UUID lookup table | total_objects=%d", len(uuid_lookup))

    populated_objects: Dict[str, Dict[str, ResolvedMiraclObj]] = {
        cls_name: {attr_name: obj for attr_name, obj in attrs.items()}
        for cls_name, attrs in resolved_objects.items()
    }

    updated_count = 0

    for key, value in parsed_args.items():
        # NOTE: This is where the non-UUID keys (injected argparse internals or GUI
        # framework stuff) are skipped. As mentioned in the docstring, MIRACL arg keys
        # are ALWAYS UUID strings set via dest=str(resolved.id).
        if not _is_uuid(key):
            logger.debug("Skipping non-UUID key | key=%s", key)
            continue

        if key not in uuid_lookup:
            raise RuntimeError(
                f"UUID '{key}' from parsed args has no matching ResolvedMiraclObj. The serializer and deserializer were likely called with different resolved_objects instances. This is a pipeline assembly error."
            )

        class_name, attr_name, obj = uuid_lookup[key]

        # NOTE: Original is frozen hence why we do model_copy here.
        updated_obj = obj.model_copy(update={"content": value})
        populated_objects[class_name][attr_name] = updated_obj

        updated_count += 1
        logger.debug(
            "Updated ResolvedMiraclObj | class=%s | attr=%s | value=%s",
            class_name,
            attr_name,
            value,
        )

    logger.info("Deserialization complete | updated_objects=%d", updated_count)

    return populated_objects
