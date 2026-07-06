from typing import cast

import numpy as np

from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_types import ImagePixels

from .._views.cropped_object import CroppedObject


def crop_objects(
    pixels: ImagePixels,
    detected_objects: list[DetectedObject],
) -> list[CroppedObject]:
    pixels = np.asarray(pixels)
    height, width = pixels.shape[:2]

    cropped_objects: list[CroppedObject] = []

    for detected_object in detected_objects:
        x1 = _clamp(round(detected_object.bbox[0] * width), 0, width)
        y1 = _clamp(round(detected_object.bbox[1] * height), 0, height)
        x2 = _clamp(round(detected_object.bbox[2] * width), 0, width)
        y2 = _clamp(round(detected_object.bbox[3] * height), 0, height)

        if x2 < x1:
            x1, x2 = x2, x1

        if y2 < y1:
            y1, y2 = y2, y1

        crop = cast(ImagePixels, np.ascontiguousarray(pixels[y1:y2, x1:x2]))
        crop_width = x2 - x1
        crop_height = y2 - y1

        keypoints = [
            [
                (kx * width - x1) / crop_width if crop_width > 0 else 0.0,
                (ky * height - y1) / crop_height if crop_height > 0 else 0.0,
            ]
            for kx, ky in detected_object.keypoints
        ]

        cropped_objects.append(
            CroppedObject(
                pixels=crop,
                score=detected_object.score,
                label=detected_object.label,
                keypoint_type=detected_object.keypoint_type,
                keypoints=keypoints,
            )
        )

    return cropped_objects


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))
