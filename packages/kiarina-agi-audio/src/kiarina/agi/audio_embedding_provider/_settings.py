from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.audio_embedding_provider_name import AudioEmbeddingProviderName


class AudioEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_EMBEDDING_PROVIDER_",
        extra="ignore",
    )

    presets: dict[AudioEmbeddingProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.audio_embedding_provider_impl.mock:create_mock_audio_embedding_provider",
            "ecapa-tdnn-onnx": "kiarina.agi.audio_embedding_provider_impl.ecapa_tdnn_onnx:create_ecapa_tdnn_onnx_audio_embedding_provider",
            "clap-onnx": "kiarina.agi.audio_embedding_provider_impl.clap_onnx:create_clap_onnx_audio_embedding_provider",
        }
    )

    customs: dict[AudioEmbeddingProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(AudioEmbeddingProviderSettings)
