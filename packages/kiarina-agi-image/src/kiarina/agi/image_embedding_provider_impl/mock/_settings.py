from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    kind: str = "image"
    space_id: str | None = None
    dimension: int = 3
    embedding: list[float] = Field(default_factory=lambda: [1.0, 0.0, 0.0])
    normalize_embedding: bool = True


settings_manager = SettingsManager(MockImageEmbeddingProviderSettings)
