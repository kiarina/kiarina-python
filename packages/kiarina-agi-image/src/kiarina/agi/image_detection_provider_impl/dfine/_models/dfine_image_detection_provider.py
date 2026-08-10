import json
from pathlib import Path

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import (
    BaseImageDetectionProvider,
    DetectedObject,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import DFineImageDetectionProviderSettings

try:
    import cv2
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime and opencv-python are required to use "
        "DFineImageDetectionProvider. "
        "Install them with: pip install 'kiarina-agi-image[image-detection-provider-dfine]'"
    ) from exc


class DFineImageDetectionProvider(BaseImageDetectionProvider):
    def __init__(self, settings: DFineImageDetectionProviderSettings) -> None:
        super().__init__()

        self.settings: DFineImageDetectionProviderSettings = settings
        self._session: ort.InferenceSession | None = None
        self._labels: list[str] | None = None
        self._model_path: Path | None = None
        self._label_map_path: Path | None = None
        self._config_path: Path | None = None

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
                    / "dfine"
                    / self.settings.model_filename,
                )

        return self._model_path

    def _resolve_config_path(self) -> Path:
        if self._config_path is None:
            self._config_path = download_file(
                self.settings.config_url,
                self.settings.config_sha256,
                user_directory.get_user_cache_dir()
                / "models"
                / "dfine"
                / self.settings.config_filename,
            )

        return self._config_path

    def _resolve_label_map_path(self) -> Path:
        if self._label_map_path is None:
            if self.settings.label_map_path is not None:
                self._label_map_path = Path(self.settings.label_map_path).expanduser()
            else:
                raise ValueError("label_map_path is not set")

        return self._label_map_path

    @property
    def session(self) -> ort.InferenceSession:
        if self._session is None:
            self._session = ort.InferenceSession(str(self._resolve_model_path()))

        return self._session

    @property
    def labels(self) -> list[str]:
        if self._labels is None:
            if self.settings.label_map_path is not None:
                self._labels = _load_label_map(self._resolve_label_map_path())
            else:
                self._labels = _create_labels(self._resolve_config_path())

        return self._labels

    def _detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        input_size = self.settings.input_size
        resized = cv2.resize(pixels, (input_size, input_size))
        image = resized.astype(np.float32) / 255.0
        image = np.transpose(image, (2, 0, 1))[np.newaxis, ...]

        logits, boxes = self._run(image)

        scores = _sigmoid(logits)
        class_ids = scores.argmax(axis=1)
        best_scores = scores.max(axis=1)

        detections: list[DetectedObject] = []

        for class_id, box, score in zip(class_ids, boxes, best_scores, strict=True):
            if score < self.settings.score_threshold:
                continue

            cx, cy, w, h = (float(value) for value in box)

            detections.append(
                DetectedObject(
                    bbox=[cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                    score=float(score),
                    label=self._resolve_label(int(class_id)),
                )
            )

        return detections

    def _run(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        outputs = self.session.run(None, {self.settings.image_input_name: image})

        index_by_name = {
            output.name: position
            for position, output in enumerate(self.session.get_outputs())
        }

        logits = outputs[index_by_name[self.settings.logits_output_name]]
        boxes = outputs[index_by_name[self.settings.boxes_output_name]]

        return (
            np.asarray(logits).reshape(-1, np.asarray(logits).shape[-1]),
            np.asarray(boxes).reshape(-1, 4),
        )

    def _resolve_label(self, class_id: int) -> str:
        labels = self.labels

        if 0 <= class_id < len(labels):
            return labels[class_id]

        return str(class_id)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def _load_label_map(path: Path) -> list[str]:
    labels: list[str] = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            label = line.strip()

            if label:
                labels.append(label)

    if not labels:
        raise ValueError(f"Label map is empty: {path}")

    return labels


def _create_labels(config_path: Path) -> list[str]:
    with open(config_path, encoding="utf-8") as file:
        config = json.load(file)

    id_to_label = {int(key): value for key, value in config["id2label"].items()}
    return [id_to_label[index] for index in range(len(id_to_label))]
