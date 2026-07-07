from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

_MODEL_REVISION = "ba1f3b0843f24bc5417d38e19c37b287d719b2f4"
_MODEL_FILENAME = "vision_model_int8.onnx"


class SigLIP2ImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_SIGLIP2_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    model_url: str = (
        "https://huggingface.co/onnx-community/siglip2-base-patch16-224-ONNX/"
        f"resolve/{_MODEL_REVISION}/onnx/{_MODEL_FILENAME}"
    )

    model_sha256: str = (
        "0dd31785a2713f1113ef2272472165c69d580473dae38d7b47568ac587795e70"
    )

    model_filename: str = _MODEL_FILENAME

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
