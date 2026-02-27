# from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
# from miracl.system.objs.objs_conv.objs_tiff_to_nii.objs_tiff_to_nii import (
#     ConvTiffNiiObjs,
# )
# from miracl.system.datamodels.miraclobj_enums import ModuleType
#
# from miracl.system.objs.objs_seg.objs_mapl3 import objs_mapl3_interface_folder
# from typing import Dict, Type
# from uuid import UUID
#
#
# def argparser_serializer(cls: Type[MiraclObj], flow: ModuleType) -> Dict[str, Dict]:
#     selected_data = {}
#
#     for name in dir(cls):
#         attr = getattr(cls, name)
#         if isinstance(attr, MiraclObj):
#             if flow == ModuleType.MODULE:
#                 include = {
#                     "id",
#                     "name",
#                     "cli_s_flag",
#                     "cli_l_flag",
#                     "cli_obj_type",
#                     "cli_help",
#                     "obj_default",
#                     "cli_required",
#                     "content",
#                 }
#             else:
#                 include = {"id": True, "name": True, "flow": {flow}, "content": True}
#
#             selected_data[name] = attr.model_dump(include=include)
#
#     return selected_data
#
#
# def argparser_deserializer(cls: Type[MiraclObj], updated_data: Dict[str, Dict]):
#     """
#     Given a class and a dictionary of updated data from argparser_serializer(),
#     update each corresponding MiraclObj using model_copy(update=...) and replace
#     the object in the class by matching UUIDs.
#     """
#     id_to_attr: Dict[UUID, str] = {}
#
#     for name in dir(cls):
#         attr = getattr(cls, name)
#         if isinstance(attr, MiraclObj) and hasattr(attr, "id"):
#             id_to_attr[attr.id] = name
#
#     for data in updated_data.values():
#         try:
#             obj_id = data["id"]
#         except KeyError as e:
#             raise KeyError(f"[Error] Invalid or missing ID in data: {e}")
#
#         attr_name = id_to_attr.get(obj_id)
#         if attr_name:
#             original_obj = getattr(cls, attr_name)
#
#             updated_obj = original_obj.model_copy(update=data)
#
#             setattr(cls, attr_name, updated_obj)
#         else:
#             raise ValueError(f"[Warning] No object found with id: {obj_id}")

from typing import Dict, Type, Any
from uuid import UUID

from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.objs.objs_conv.objs_tiff_to_nii.objs_tiff_to_nii import (
    ConvTiffNiiObjs,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType
from miracl.system.objs.objs_seg.objs_mapl3 import objs_mapl3_interface_folder


def argparser_serializer(
    cls: Type[MiraclObj], flow: ModuleType
) -> Dict[str, Dict[str, Any]]:
    """
    Serialize MiraclObj attributes of a class into dictionaries suitable for CLI argument parsing.

    Args:
        cls (Type[MiraclObj]): Class containing MiraclObj attributes.
        flow (ModuleType): ModuleType enum indicating context (e.g., MODULE or workflow).

    Returns:
        Dict[str, Dict[str, Any]]: Mapping of attribute names to serialized dict representations,
        filtered by fields depending on the flow type.
    """
    selected_data: Dict[str, Dict[str, Any]] = {}

    for name in dir(cls):
        attr = getattr(cls, name)
        if isinstance(attr, MiraclObj):
            if flow == ModuleType.MODULE:
                include = {
                    "id",
                    "name",
                    "cli_s_flag",
                    "cli_l_flag",
                    "cli_obj_type",
                    "cli_help",
                    "cli_metavar",
                    "cli_nargs",
                    "cli_choices",
                    "obj_default",
                    "cli_required",
                    "cli_action",
                    "content",
                }
            else:
                include = {
                    "id": True,
                    "name": True,
                    "flow": {flow},
                    "content": True,
                }

            selected_data[name] = attr.model_dump(include=include)

    return selected_data


def argparser_deserializer(
    cls: Type[MiraclObj], updated_data: Dict[str, Dict[str, Any]]
) -> None:
    """
    Deserialize updated dict data (from argparser_serializer) back into MiraclObj instances,
    updating each object by matching its UUID and replacing it on the class attribute.

    Args:
        cls (Type[MiraclObj]): Class containing MiraclObj attributes to update.
        updated_data (Dict[str, Dict[str, Any]]): Dict of attribute names to updated data dicts.

    Raises:
        KeyError: If an expected 'id' key is missing in any data dict.
        ValueError: If no MiraclObj is found matching the UUID in updated data.
    """
    id_to_attr: Dict[UUID, str] = {}

    # Build a lookup of UUID -> attribute name for quick access
    for name in dir(cls):
        attr = getattr(cls, name)
        if isinstance(attr, MiraclObj) and hasattr(attr, "id"):
            id_to_attr[attr.id] = name

    for data in updated_data.values():
        try:
            obj_id: UUID = data["id"]  # Assume it's already a UUID instance
        except KeyError as e:
            raise KeyError(f"[Error] Invalid or missing ID in data: {e}")

        attr_name = id_to_attr.get(obj_id)
        if attr_name:
            original_obj = getattr(cls, attr_name)
            updated_obj = original_obj.model_copy(update=data)
            setattr(cls, attr_name, updated_obj)
        else:
            raise ValueError(f"[Warning] No object found with id: {obj_id}")


serialized = argparser_serializer(ConvTiffNiiObjs, ModuleType.MODULE)

serialized["tiff_folder"]["content"] = "My new content"

argparser_deserializer(ConvTiffNiiObjs, serialized)

serialized = argparser_serializer(ConvTiffNiiObjs, ModuleType.MODULE)["tiff_folder"]

# print(serialized)
