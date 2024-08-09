from datamodel_env_vars import get_settings
from miracl.system.objs.objs_reg import RegClarAllenObjs as reg_clar_allen

# Get the settings
settings = get_settings()

# Access specific settings
miracl_home = settings.folders.MIRACL_HOME
atlases_home = settings.folders.ATLASES_HOME
version = settings.versions.VERSION

# Use the settings in your code
print(f"MIRACL home directory: {miracl_home}")
print(f"Current version: {version}")

# You can also access nested settings directly
ara_home = settings.folders.ARA_HOME
print(f"ARA home directory: {ara_home}")
print(f"Atlases home: {atlases_home}")

# Dict
all_settings = settings.model_dump()
print(all_settings["folders"]["ATLASES_HOME"])

# Safely accessing the nested settings using get
folders = all_settings.get(
    "folders", {}
)  # Default to an empty dict if "folders" is not found
atlases_home_dir = folders.get(
    "ATLASES_HOME"
)  # This will return None if "ATLASES_HOME" is not found

if atlases_home_dir is not None:
    print(f"Atlases home directory: {atlases_home_dir}")
else:
    print("ATLASES_HOME is not set.")

print(reg_clar_allen.orient_code.cli_s_flag)
