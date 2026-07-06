from pathlib import Path
from threading import Lock

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import (
    BaseImageDetectionProvider,
    DetectedObject,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._settings import YuNetImageDetectionProviderSettings

try:
    import cv2
except ImportError as exc:
    raise ImportError(
        "opencv-python is required to use YuNetImageDetectionProvider. "
        "Install it with: pip install 'kiarina-agi-image[image-detection-provider-yunet]'"
    ) from exc

_KEYPOINT_TYPE = "face_5pt"

# YuNet's native landmark order is
#   [right eye, left eye, nose, right mouth corner, left mouth corner]
# where "right"/"left" are the subject's anatomical sides. In image space the
# subject's right eye is on the image-left, so the native order is already
# image-left to image-right, which matches the ArcFace/SCRFD face_5pt template
# (index0 = image-left eye). No reordering is needed; we just pick the (x, y)
# pairs in their native column positions within the 15-value row.
_FACE_5PT_COLUMNS = [(4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]


class YuNetImageDetectionProvider(BaseImageDetectionProvider):
    def __init__(self, settings: YuNetImageDetectionProviderSettings) -> None:
        super().__init__()

        self.settings: YuNetImageDetectionProviderSettings = settings
        self._detector: cv2.FaceDetectorYN | None = None
        self._lock = Lock()

    @property
    def detector(self) -> "cv2.FaceDetectorYN":
        if self._detector is None:
            if self.settings.model_path is None:
                raise ValueError(
                    "model_path must be set for YuNetImageDetectionProvider"
                )

            model_path = Path(self.settings.model_path).expanduser()
            self._detector = cv2.FaceDetectorYN.create(
                str(model_path),
                "",
                (0, 0),
                self.settings.score_threshold,
                self.settings.nms_threshold,
                self.settings.top_k,
            )

        return self._detector

    def _detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        height, width = pixels.shape[:2]
        image = self._to_bgr(pixels)

        with self._lock:
            detector = self.detector
            detector.setInputSize((width, height))
            _, faces = detector.detect(image)

        if faces is None:
            return []

        detections: list[DetectedObject] = []

        for face in faces:
            x, y, w, h = (float(value) for value in face[:4])
            score = float(face[14])

            keypoints = [
                self._normalize_point(float(face[xi]), float(face[yi]), width, height)
                for xi, yi in _FACE_5PT_COLUMNS
            ]

            detections.append(
                DetectedObject(
                    bbox=self._normalize_bbox(x, y, x + w, y + h, width, height),
                    score=score,
                    label=self.settings.label,
                    keypoint_type=_KEYPOINT_TYPE,
                    keypoints=keypoints,
                )
            )

        return detections

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"
