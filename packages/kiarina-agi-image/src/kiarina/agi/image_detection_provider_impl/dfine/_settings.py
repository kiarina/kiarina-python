from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class DFineImageDetectionProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_DFINE_",
        extra="ignore",
    )

    # NOTE: onnx-community/dfine_s_coco-ONNX (Transformers / RTDetrImageProcessor export)
    model_path: str | Path | None = None

    # One label per line; line number (0-based) is the class id.
    label_map_path: str | Path | None = None

    input_size: int = 640

    score_threshold: float = 0.5

    image_input_name: str = "pixel_values"

    logits_output_name: str = "logits"

    boxes_output_name: str = "pred_boxes"


settings_manager = SettingsManager(DFineImageDetectionProviderSettings)
