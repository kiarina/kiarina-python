from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class KiapiImageGenerationProviderSettings(BaseSettings):
    """Settings for image generation through kiapi."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_GENERATION_PROVIDER_IMPL_KIAPI_",
        extra="ignore",
    )

    kiapi_base_url: str = Field(
        default="http://localhost:8000",
        title="kiapi Base URL",
        description="Base URL of the kiapi server.",
    )
    family: Literal["flux2", "qwen", "ernie"] = Field(
        default="qwen",
        title="Image Family",
        description="kiapi image family used for generation and editing.",
    )
    timeout: float = Field(
        default=1800.0,
        title="Timeout",
        description="HTTP request timeout in seconds.",
    )
    extra_params: dict[str, Any] = Field(
        default_factory=dict,
        title="Extra Parameters",
        description="Additional parameters included in kiapi image requests.",
    )


settings_manager = SettingsManager(KiapiImageGenerationProviderSettings)
