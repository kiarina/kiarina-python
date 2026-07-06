from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SigLIP2ImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_SIGLIP2_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    kind: str = "object"

    dimension: int = 768

    input_size: int = 224

    # SigLIP normalizes with mean/std 0.5 per channel (i.e. (x/255 - 0.5) / 0.5).
    image_mean: list[float] = Field(default_factory=lambda: [0.5, 0.5, 0.5])

    image_std: list[float] = Field(default_factory=lambda: [0.5, 0.5, 0.5])

    image_input_name: str = "pixel_values"

    # SigLIP2 vision model exposes "last_hidden_state" and "pooler_output";
    # the pooled output is the image embedding.
    output_name: str | None = "pooler_output"

    normalize_embedding: bool = True


settings_manager = SettingsManager(SigLIP2ImageEmbeddingProviderSettings)
