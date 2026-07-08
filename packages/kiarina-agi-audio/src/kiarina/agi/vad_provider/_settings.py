from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.vad_provider_name import VADProviderName


class VADProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VAD_PROVIDER_",
        extra="ignore",
    )

    presets: dict[VADProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.vad_provider_impl.mock:create_mock_vad_provider",
            "silero": "kiarina.agi.vad_provider_impl.silero:create_silero_vad_provider",
        }
    )

    customs: dict[VADProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(VADProviderSettings)
