import numpy as np

from kiarina.agi.image_detection_model import crop_objects
from kiarina.agi.image_detection_provider import DetectedObject


def _gradient_image(height: int, width: int) -> np.ndarray:
    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    pixels[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)
    pixels[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, np.newaxis]
    return pixels


def test_crop_objects_crops_bbox() -> None:
    pixels = _gradient_image(100, 200)  # H=100, W=200

    detected = [
        DetectedObject(bbox=[0.25, 0.10, 0.75, 0.60], score=0.8, label="dog"),
    ]

    cropped = crop_objects(pixels, detected)

    assert len(cropped) == 1
    crop = cropped[0]
    # x: 0.25*200=50 .. 0.75*200=150 -> width 100; y: 0.10*100=10 .. 0.60*100=60 -> 50
    assert crop.pixels.shape == (50, 100, 3)
    assert crop.pixels.dtype == np.uint8
    assert crop.score == 0.8
    assert crop.label == "dog"
    # crop must be an independent copy of the source region.
    assert np.array_equal(crop.pixels, pixels[10:60, 50:150])


def test_crop_objects_keypoints_relative_to_bbox() -> None:
    pixels = _gradient_image(100, 100)

    detected = [
        DetectedObject(
            bbox=[0.20, 0.20, 0.80, 0.80],
            score=0.9,
            label="face",
            keypoint_type="face_5pt",
            keypoints=[[0.50, 0.50], [0.20, 0.20], [0.80, 0.80]],
        ),
    ]

    crop = crop_objects(pixels, detected)[0]

    # center of bbox -> (0.5, 0.5); top-left corner -> (0, 0); bottom-right -> (1, 1)
    assert crop.keypoints[0] == [0.5, 0.5]
    assert crop.keypoints[1] == [0.0, 0.0]
    assert crop.keypoints[2] == [1.0, 1.0]
    assert crop.keypoint_type == "face_5pt"


def test_crop_objects_clamps_to_image_bounds() -> None:
    pixels = _gradient_image(40, 40)

    detected = [
        DetectedObject(bbox=[-0.5, -0.5, 1.5, 1.5], score=0.5, label="x"),
    ]

    crop = crop_objects(pixels, detected)[0]

    assert crop.pixels.shape == (40, 40, 3)
