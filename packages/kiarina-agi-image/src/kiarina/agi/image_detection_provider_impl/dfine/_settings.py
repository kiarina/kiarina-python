from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

_MODEL_REVISION = "a3cf03147a9b86c78475139115c8ac142577352d"


class DFineImageDetectionProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_DFINE_",
        extra="ignore",
    )

    # NOTE: onnx-community/dfine_s_coco-ONNX (Transformers / RTDetrImageProcessor export)
    model_path: str | Path | None = None

    model_url: str = (
        "https://huggingface.co/onnx-community/dfine_s_coco-ONNX/"
        f"resolve/{_MODEL_REVISION}/onnx/model.onnx"
    )

    model_sha256: str = (
        "cd8a49a945feda6d28c6304ae8ae85c2759ba1d78a5a83a22c5ce8db82ef7238"
    )

    model_filename: str = "model.onnx"

    # One label per line; line number (0-based) is the class id.
    label_map_path: str | Path | None = None

    config_url: str = (
        "https://huggingface.co/onnx-community/dfine_s_coco-ONNX/"
        f"resolve/{_MODEL_REVISION}/config.json"
    )

    config_sha256: str = (
        "9338ef3863d6e95627d4ab06009fa85b1dd523b346b5c3595de2b08862136e99"
    )

    config_filename: str = "config.json"

    input_size: int = 640

    score_threshold: float = 0.5

    image_input_name: str = "pixel_values"

    logits_output_name: str = "logits"

    boxes_output_name: str = "pred_boxes"


settings_manager = SettingsManager(DFineImageDetectionProviderSettings)
