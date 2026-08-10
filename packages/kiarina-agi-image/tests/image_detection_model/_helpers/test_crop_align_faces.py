import numpy as np

from kiarina.agi.image_detection_model import crop_align_faces
from kiarina.agi.image_detection_provider import DetectedObject

# ArcFace 112x112 template (image-left eye, image-right eye, nose, mouths).
_ARCFACE_DST = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float64,
)


def test_crop_align_faces_output_shape_and_filtering() -> None:
    pixels = np.zeros((200, 200, 3), dtype=np.uint8)

    detected = [
        DetectedObject(
            bbox=[0.1, 0.1, 0.9, 0.9],
            score=0.9,
            label="face",
            keypoint_type="face_5pt",
            keypoints=(_ARCFACE_DST / 112.0).tolist(),
        ),
        # skipped: not face_5pt
        DetectedObject(bbox=[0.0, 0.0, 1.0, 1.0], score=0.8, label="dog"),
        # skipped: face_5pt but wrong number of keypoints
        DetectedObject(
            bbox=[0.0, 0.0, 1.0, 1.0],
            score=0.7,
            label="face",
            keypoint_type="face_5pt",
            keypoints=[[0.5, 0.5]],
        ),
    ]

    aligned = crop_align_faces(pixels, detected, output_size=112)

    assert len(aligned) == 1
    assert aligned[0].shape == (112, 112, 3)
    assert aligned[0].dtype == np.uint8


def test_crop_align_faces_identity_when_keypoints_match_template() -> None:
    # When the source keypoints already equal the template (on a 112 image),
    # alignment is the identity transform, so markers stay in place.
    size = 112
    pixels = np.zeros((size, size, 3), dtype=np.uint8)

    for x, y in _ARCFACE_DST:
        pixels[round(y), round(x)] = 255

    detected = [
        DetectedObject(
            bbox=[0.0, 0.0, 1.0, 1.0],
            score=1.0,
            label="face",
            keypoint_type="face_5pt",
            keypoints=(_ARCFACE_DST / size).tolist(),
        ),
    ]

    aligned = crop_align_faces(pixels, detected, output_size=size)[0]

    # Each template marker should survive the (near-identity) warp.
    for x, y in _ARCFACE_DST:
        patch = aligned[round(y) - 1 : round(y) + 2, round(x) - 1 : round(x) + 2]
        assert patch.max() > 0


def test_crop_align_faces_recovers_scaled_translated_face() -> None:
    # Place the template into a larger image via a known scale + translation;
    # alignment must map those keypoints back onto the template positions.
    output_size = 112
    scale = 1.5
    offset = np.array([40.0, 30.0])

    src_points = _ARCFACE_DST * scale + offset
    pixels = np.zeros((300, 300, 3), dtype=np.uint8)

    detected = [
        DetectedObject(
            bbox=[0.0, 0.0, 1.0, 1.0],
            score=1.0,
            label="face",
            keypoint_type="face_5pt",
            keypoints=(src_points / 300.0).tolist(),
        ),
    ]

    # Mark the source keypoints so we can check where they land after alignment.
    for x, y in src_points:
        pixels[round(y), round(x)] = 255

    aligned = crop_align_faces(pixels, detected, output_size=output_size)[0]

    for x, y in _ARCFACE_DST:
        patch = aligned[round(y) - 2 : round(y) + 3, round(x) - 2 : round(x) + 3]
        assert patch.max() > 0
