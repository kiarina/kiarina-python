from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.backend_type import BackendType


class GeminiImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_GEMINI_",
        extra="ignore",
    )

    backend_type: BackendType = "gemini_api"

    google_auth_settings_key: SettingsKey | None = None

    vertex_ai_location: str | None = None

    # Gemini Embedding 2 — natively multimodal (text/image/audio/video/pdf).
    model_name: str = "gemini-embedding-2"

    kind: str = "seen"

    # Matryoshka output dimension. Gemini Embedding 2 supports flexible sizes;
    # normalize embeddings when using less than the native dimension.
    output_dimensionality: int = 1536

    # Optional embedding task type (e.g. "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY").
    task_type: str | None = None

    cost_microdollars_per_request: int = 100

    normalize_embedding: bool = True


settings_manager = SettingsManager(GeminiImageEmbeddingProviderSettings)
