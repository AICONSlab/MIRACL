from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class FolderSettings(BaseSettings):
    MIRACL_HOME: str = Field(
        ...,
        env="MIRACL_HOME",
    )
    ATLASES_HOME: str = Field(
        ...,
        env="ATLASES_HOME",
    )
    ARA_HOME: str = Field(
        ...,
        env="ARA_HOME",
    )


class VersionSettings(BaseSettings):
    VERSION: str = Field(
        ...,
        env="VERSION",
    )


class Settings(BaseSettings):
    folders: FolderSettings = FolderSettings()
    versions: VersionSettings = VersionSettings()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
