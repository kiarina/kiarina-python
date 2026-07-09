from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.storage_type import StorageType


class FileFactorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FILE_FACTORY_",
        extra="ignore",
    )

    storage: StorageType = "local"


settings_manager = SettingsManager(FileFactorySettings)
