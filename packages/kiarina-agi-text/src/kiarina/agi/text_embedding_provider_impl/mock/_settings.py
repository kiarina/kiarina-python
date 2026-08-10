from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockTextEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TEXT_EMBEDDING_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    kind: str = "text"
    space_id: str | None = None
    dimension: int = 3
    embedding: list[float] = Field(default_factory=lambda: [1.0, 0.0, 0.0])
    normalize_embedding: bool = True


settings_manager = SettingsManager(MockTextEmbeddingProviderSettings)
