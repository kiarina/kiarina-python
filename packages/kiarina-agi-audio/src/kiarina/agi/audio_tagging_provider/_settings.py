from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.audio_tagging_provider_name import AudioTaggingProviderName


class AudioTaggingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_TAGGING_PROVIDER_",
        extra="ignore",
    )

    presets: dict[AudioTaggingProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.audio_tagging_provider_impl.mock:create_mock_audio_tagging_provider",
            "yamnet": "kiarina.agi.audio_tagging_provider_impl.yamnet:create_yamnet_audio_tagging_provider",
        }
    )

    customs: dict[AudioTaggingProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(AudioTaggingProviderSettings)
