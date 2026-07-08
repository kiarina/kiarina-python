from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.audio_tagging_model_config import AudioTaggingModelConfig
from ._types.audio_tagging_model_alias import AudioTaggingModelAlias
from ._types.audio_tagging_model_name import AudioTaggingModelName
from ._types.audio_tagging_model_specifier import AudioTaggingModelSpecifier


class AudioTaggingModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_TAGGING_MODEL_",
        extra="ignore",
    )

    default: AudioTaggingModelSpecifier = "local"

    aliases: dict[AudioTaggingModelAlias, AudioTaggingModelName] = Field(
        default_factory=lambda: {
            "local": "yamnet",
        }
    )

    presets: dict[AudioTaggingModelName, AudioTaggingModelConfig] = Field(
        default_factory=lambda: {
            "mock": AudioTaggingModelConfig(provider_name="mock"),
            "yamnet": AudioTaggingModelConfig(
                provider_name="yamnet",
            ),
        }
    )

    customs: dict[AudioTaggingModelName, AudioTaggingModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(AudioTaggingModelSettings)
