from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.audio_embedding_model_config import AudioEmbeddingModelConfig
from ._types.audio_embedding_model_alias import AudioEmbeddingModelAlias
from ._types.audio_embedding_model_name import AudioEmbeddingModelName
from ._types.audio_embedding_model_specifier import AudioEmbeddingModelSpecifier


class AudioEmbeddingModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_EMBEDDING_MODEL_",
        extra="ignore",
    )

    default: AudioEmbeddingModelSpecifier = "mock"

    aliases: dict[AudioEmbeddingModelAlias, AudioEmbeddingModelName] = Field(
        default_factory=lambda: {
            "speaker": "ecapa-tdnn",
            "sound": "clap",
        }
    )

    presets: dict[AudioEmbeddingModelName, AudioEmbeddingModelConfig] = Field(
        default_factory=lambda: {
            "mock": AudioEmbeddingModelConfig(provider_name="mock"),
            "ecapa-tdnn": AudioEmbeddingModelConfig(
                provider_name="ecapa-tdnn-onnx",
            ),
            "clap": AudioEmbeddingModelConfig(
                provider_name="clap-onnx",
            ),
        }
    )

    customs: dict[AudioEmbeddingModelName, AudioEmbeddingModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(AudioEmbeddingModelSettings)
