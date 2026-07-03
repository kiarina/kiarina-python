from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.backend_type import BackendType


class GoogleTextEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TEXT_EMBEDDING_PROVIDER_IMPL_GOOGLE_",
        extra="ignore",
    )

    backend_type: BackendType = "gemini_api"

    google_auth_settings_key: SettingsKey | None = None

    vertex_ai_location: str | None = None

    model_name: str = "gemini-embedding-2"

    kind: str = "text"

    dimension: int = 1536

    task_type: str | None = None

    max_char_count: int = 16_000

    cost_microdollars_per_request: int = 100

    normalize_embedding: bool = True


settings_manager = SettingsManager(GoogleTextEmbeddingProviderSettings)
