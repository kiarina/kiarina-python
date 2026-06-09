from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class CloudflareSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_CLOUDFLARE_")

    account_id: str

    api_token: SecretStr


settings_manager = SettingsManager(CloudflareSettings, multi=True)
