from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager


class OpenAITextEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TEXT_EMBEDDING_PROVIDER_IMPL_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    model_name: str = "text-embedding-3-large"
    kind: str = "text"
    dimension: int = 3072
    max_token_count: int = 8192
    cost_microdollars_per_1k_tokens: int = 130
    timeout: float | None = 120.0
    normalize_embedding: bool = True


settings_manager = SettingsManager(OpenAITextEmbeddingProviderSettings)
