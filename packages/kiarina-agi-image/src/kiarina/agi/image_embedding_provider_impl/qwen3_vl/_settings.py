from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class Qwen3VLImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_QWEN3_VL_",
        extra="ignore",
    )

    # Base URL of the standalone MLX embedding server (see models/qwen3-vl-embedding).
    base_url: str = "http://localhost:8900"

    model_id: str = "mlx-community/Qwen3-VL-Embedding-2B-mxfp8"

    kind: str = "seen"

    dimension: int = 2048

    timeout: float = 60.0

    normalize_embedding: bool = True


settings_manager = SettingsManager(Qwen3VLImageEmbeddingProviderSettings)
