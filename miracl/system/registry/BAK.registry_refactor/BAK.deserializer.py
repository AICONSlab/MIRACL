from typing import Union, List, Dict, Any, Optional
from argparse import Namespace
from uuid import UUID
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj


def deserialize_parsed_args_to_objects(
    parsed_args: Union[Namespace, Dict[str, Any]],
    miracl_objs: Optional[List[MiraclObj]] = None,
    strict: bool = True,
) -> List[MiraclObj]:
    """
    Assign parsed CLI arguments to MiraclObj.content by matching UUIDs.

    Args:
        parsed_args: Parsed CLI arguments from argparse
        miracl_objs: List of MiraclObj instances to populate.
                     If None, uses all registered instances from MiraclObj.instances
        strict: If True, raise error for unmatched UUIDs; if False, skip silently

    Returns:
        Updated list of MiraclObj instances (same objects, mutated in-place)

    Raises:
        ValueError: If strict=True and a UUID in parsed_args doesn't match any object
    """
    # Convert Namespace to dict if needed
    if isinstance(parsed_args, Namespace):
        parsed_args = vars(parsed_args)

    # Use all registered instances if not provided
    if miracl_objs is None:
        miracl_objs = list(MiraclObj.instances.values())

    # Build UUID lookup (use UUID objects, not strings)
    uuid_to_obj: Dict[UUID, MiraclObj] = {}
    for obj in miracl_objs:
        uuid_to_obj[obj.id] = obj

    # Process each parsed argument
    for uuid_str, value in parsed_args.items():
        # Convert string to UUID for type safety
        try:
            uuid = UUID(uuid_str)
        except ValueError:
            if strict:
                raise ValueError(f"Invalid UUID format in parsed args: '{uuid_str}'")
            continue

        # Look up object
        obj = uuid_to_obj.get(uuid)

        if obj is None:
            if strict:
                raise ValueError(
                    f"No MiraclObj found for UUID {uuid}. "
                    f"This indicates a mismatch between serializer and deserializer."
                )
            continue

        # Assign value (Pydantic validator handles type conversion)
        obj.content = value

    return miracl_objs
