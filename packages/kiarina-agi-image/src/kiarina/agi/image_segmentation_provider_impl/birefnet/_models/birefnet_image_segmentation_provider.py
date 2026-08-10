from pathlib import Path

import cv2
import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_segmentation_provider import (
    BaseImageSegmentationProvider,
    ImageSegmentationResult,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import BiRefNetImageSegmentationProviderSettings

try:
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime is required to use BiRefNetImageSegmentationProvider. "
        "Install it with: "
        "pip install 'kiarina-agi-image[image-segmentation-provider-birefnet]'"
    ) from exc


class BiRefNetImageSegmentationProvider(BaseImageSegmentationProvider):
    def __init__(self, settings: BiRefNetImageSegmentationProviderSettings) -> None:
        super().__init__()
        self.settings = settings
        self._session: ort.InferenceSession | None = None
        self._model_path: Path | None = None

    def _resolve_model_path(self) -> Path:
        if self._model_path is None:
            if self.settings.model_path is not None:
                self._model_path = Path(self.settings.model_path).expanduser()
            else:
                self._model_path = download_file(
                    self.settings.model_url,
                    self.settings.model_sha256,
                    user_directory.get_user_cache_dir()
                    / "models"
                    / "birefnet"
                    / self.settings.model_filename,
                )
        return self._model_path

    @property
    def session(self) -> ort.InferenceSession:
        if self._session is None:
            self._session = ort.InferenceSession(
                str(self._resolve_model_path()),
                providers=self.settings.execution_providers,
            )
        return self._session

    def _segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageSegmentationResult:
        input_tensor = self._preprocess(pixels)
        logits = self.session.run(
            [self.settings.output_name],
            {self.settings.image_input_name: input_tensor},
        )[0]
        confidence_map = self._postprocess(logits, pixels.shape[:2])
        mask = np.where(confidence_map >= self.settings.threshold, 255, 0).astype(
            np.uint8
        )
        return ImageSegmentationResult(
            mask=np.ascontiguousarray(mask),
            confidence_map=confidence_map,
        )

    def _preprocess(self, pixels: ImagePixels) -> np.ndarray:
        size = self.settings.input_size
        resized = cv2.resize(
            pixels,
            (size, size),
            interpolation=cv2.INTER_LINEAR,
        )
        image = resized.astype(np.float32) / 255.0
        mean = np.asarray(self.settings.image_mean, dtype=np.float32)
        std = np.asarray(self.settings.image_std, dtype=np.float32)
        image = (image - mean) / std
        image = np.transpose(image, (2, 0, 1))[np.newaxis, ...]
        return np.ascontiguousarray(image, dtype=np.float32)

    @staticmethod
    def _postprocess(logits: np.ndarray, image_shape: tuple[int, int]) -> np.ndarray:
        values = np.asarray(logits, dtype=np.float32).squeeze()
        confidence_map = np.asarray(
            1.0 / (1.0 + np.exp(-np.clip(values, -80.0, 80.0))),
            dtype=np.float32,
        )
        height, width = image_shape
        resized = cv2.resize(
            confidence_map,
            (width, height),
            interpolation=cv2.INTER_LINEAR,
        )
        return np.ascontiguousarray(resized, dtype=np.float32)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"
