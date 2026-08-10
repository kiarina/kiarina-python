from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class BiRefNetImageSegmentationProviderSettings(BaseSettings):
    """Settings for BiRefNet ONNX image segmentation."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_SEGMENTATION_PROVIDER_IMPL_BIREFNET_",
        extra="ignore",
    )

    model_path: str | Path | None = Field(
        default=None,
        title="Model Path",
        description="Local ONNX model path. The default model is downloaded when unset.",
    )
    model_url: str = Field(
        default=(
            "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/"
            "BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx"
        ),
        title="Model URL",
        description="URL used to download the default ONNX model.",
    )
    model_sha256: str = Field(
        default=("5600024376f572a557870a5eb0afb1e5961636bef4e1e22132025467d0f03333"),
        title="Model SHA-256",
        description="Expected SHA-256 digest of the default ONNX model.",
    )
    model_filename: str = Field(
        default="BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx",
        title="Model Filename",
        description="Filename used for the cached ONNX model.",
    )
    input_size: int = Field(
        default=1024,
        gt=0,
        title="Input Size",
        description="Square model input size in pixels.",
    )
    threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        title="Mask Threshold",
        description="Foreground confidence threshold used to create the binary mask.",
    )
    image_mean: list[float] = Field(
        default_factory=lambda: [0.485, 0.456, 0.406],
        min_length=3,
        max_length=3,
        title="Image Mean",
        description="RGB normalization mean.",
    )
    image_std: list[float] = Field(
        default_factory=lambda: [0.229, 0.224, 0.225],
        min_length=3,
        max_length=3,
        title="Image Standard Deviation",
        description="RGB normalization standard deviation.",
    )
    image_input_name: str = Field(
        default="input_image",
        title="Image Input Name",
        description="ONNX input tensor name.",
    )
    output_name: str = Field(
        default="output_image",
        title="Output Name",
        description="ONNX output tensor name.",
    )
    execution_providers: list[str] = Field(
        default_factory=lambda: ["CPUExecutionProvider"],
        title="Execution Providers",
        description="ONNX Runtime execution providers in priority order.",
    )


settings_manager = SettingsManager(BiRefNetImageSegmentationProviderSettings)
