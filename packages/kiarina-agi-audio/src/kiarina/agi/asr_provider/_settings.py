from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.asr_provider_name import ASRProviderName


class ASRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASR_PROVIDER_",
        extra="ignore",
    )

    presets: dict[ASRProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.asr_provider_impl.mock:create_mock_asr_provider",
            "command": "kiarina.agi.asr_provider_impl.command:create_command_asr_provider",
            "openai": "kiarina.agi.asr_provider_impl.openai:create_openai_asr_provider",
            "google": "kiarina.agi.asr_provider_impl.google:create_google_asr_provider",
        }
    )

    customs: dict[ASRProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ASRProviderSettings)
