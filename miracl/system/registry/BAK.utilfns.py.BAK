from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj


# NOTE: Move to serializer
def build_flag_map_from_class(obj_class) -> dict:
    mapping = {}
    for attr_name, attr_value in vars(obj_class).items():
        if isinstance(attr_value, MiraclObj):
            mapping[f"--{attr_value.cli_l_flag}"] = attr_value.obj_default
    return mapping
