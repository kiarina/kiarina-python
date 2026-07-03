from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.text_embedding_model_config import TextEmbeddingModelConfig
from ._types.text_embedding_model_alias import TextEmbeddingModelAlias
from ._types.text_embedding_model_name import TextEmbeddingModelName
from ._types.text_embedding_model_specifier import TextEmbeddingModelSpecifier


class TextEmbeddingModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TEXT_EMBEDDING_MODEL_",
        extra="ignore",
    )

    default: TextEmbeddingModelSpecifier = "mock"

    aliases: dict[TextEmbeddingModelAlias, TextEmbeddingModelName] = Field(
        default_factory=lambda: {
            "local": "qwen3-embedding-8b-mxfp8",
            "openai": "text-embedding-3-small",
            "google": "gemini-embedding-2",
        }
    )

    presets: dict[TextEmbeddingModelName, TextEmbeddingModelConfig] = Field(
        default_factory=lambda: {
            # --------------------------------------------------
            # mock
            # --------------------------------------------------
            "mock": TextEmbeddingModelConfig(provider_name="mock"),
            # --------------------------------------------------
            # local
            # --------------------------------------------------
            "qwen3-embedding-8b-mxfp8": TextEmbeddingModelConfig(
                provider_name="openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "Qwen3-Embedding-8B-mxfp8",
                    "dimension": 4096,
                    "cost_microdollars_per_1k_tokens": 0,
                },
            ),
            # --------------------------------------------------
            # openai
            # --------------------------------------------------
            "text-embedding-3-small": TextEmbeddingModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "text-embedding-3-small",
                    "dimension": 1536,
                    "cost_microdollars_per_1k_tokens": 20,
                },
            ),
            "text-embedding-3-large": TextEmbeddingModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "text-embedding-3-large",
                    "dimension": 3072,
                    "cost_microdollars_per_1k_tokens": 130,
                },
            ),
            # --------------------------------------------------
            # google
            # --------------------------------------------------
            "gemini-embedding-2": TextEmbeddingModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-embedding-2",
                    "dimension": 1536,
                },
            ),
        }
    )

    customs: dict[TextEmbeddingModelName, TextEmbeddingModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(TextEmbeddingModelSettings)
