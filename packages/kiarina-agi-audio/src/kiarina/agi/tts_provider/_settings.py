from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.tts_provider_name import TTSProviderName


class TTSProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TTS_PROVIDER_",
        extra="ignore",
    )

    presets: dict[TTSProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.tts_provider_impl.mock:create_mock_tts_provider",
            "command": "kiarina.agi.tts_provider_impl.command:create_command_tts_provider",
            "openai": "kiarina.agi.tts_provider_impl.openai:create_openai_tts_provider",
            "google": "kiarina.agi.tts_provider_impl.google:create_google_tts_provider",
        }
    )

    customs: dict[TTSProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(TTSProviderSettings)
