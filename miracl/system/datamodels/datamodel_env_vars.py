from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class FolderSettings(BaseSettings):
    MIRACL_HOME: str = Field(
        ...,
        env="MIRACL_HOME",
        description="MIRACL code folder",
    )
    ATLASES_HOME: str = Field(
        ...,
        env="ATLASES_HOME",
        description="Reference atlases base folder",
    )
    ARA_HOME: str = Field(
        ...,
        env="ARA_HOME",
        description="Allan Reference Atlas (ARA) folder",
    )


class VersionSettings(BaseSettings):
    VERSION: str = Field(
        ...,
        env="VERSION",
        description="MIRACL version",
    )


class Settings(BaseSettings):
    folders: FolderSettings = FolderSettings()
    versions: VersionSettings = VersionSettings()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
