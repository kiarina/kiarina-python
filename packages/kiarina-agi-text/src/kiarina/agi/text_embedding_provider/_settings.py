from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.text_embedding_provider_name import TextEmbeddingProviderName


class TextEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TEXT_EMBEDDING_PROVIDER_",
        extra="ignore",
    )

    presets: dict[TextEmbeddingProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.text_embedding_provider_impl.mock:create_mock_text_embedding_provider",
            "openai": "kiarina.agi.text_embedding_provider_impl.openai:create_openai_text_embedding_provider",
            "google": "kiarina.agi.text_embedding_provider_impl.google:create_google_text_embedding_provider",
        }
    )

    customs: dict[TextEmbeddingProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(TextEmbeddingProviderSettings)
