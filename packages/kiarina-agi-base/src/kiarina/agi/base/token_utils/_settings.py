from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class TokenUtilsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TOKEN_UTILS_",
        extra="ignore",
    )

    tiktoken_model_name: str = "gpt-4o"


settings_manager = SettingsManager(TokenUtilsSettings)
