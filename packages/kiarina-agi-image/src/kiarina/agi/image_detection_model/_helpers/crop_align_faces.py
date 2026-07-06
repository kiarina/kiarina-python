from typing import cast

import cv2
import numpy as np

from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_types import ImagePixels

_FACE_5PT = "face_5pt"

# ArcFace 5-point reference template for a 112x112 aligned face, ordered
# (image-left eye, image-right eye, nose, image-left mouth, image-right mouth).
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


def crop_align_faces(
    pixels: ImagePixels,
    detected_objects: list[DetectedObject],
    output_size: int,
) -> list[ImagePixels]:
    pixels = np.asarray(pixels)
    height, width = pixels.shape[:2]

    dst = _ARCFACE_DST * (output_size / 112.0)

    aligned_faces: list[ImagePixels] = []

    for detected_object in detected_objects:
        if detected_object.keypoint_type != _FACE_5PT:
            continue

        if len(detected_object.keypoints) != 5:
            continue

        src = np.array(
            [[kx * width, ky * height] for kx, ky in detected_object.keypoints],
            dtype=np.float64,
        )

        matrix = _umeyama(src, dst)
        aligned = cv2.warpAffine(pixels, matrix, (output_size, output_size))
        aligned_faces.append(cast(ImagePixels, aligned))

    return aligned_faces


def _umeyama(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Least-squares similarity transform (Umeyama). Returns a 2x3 affine matrix
    mapping ``src`` points onto ``dst`` points, suitable for cv2.warpAffine."""
    num, dim = src.shape

    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    src_demean = src - src_mean
    dst_demean = dst - dst_mean

    covariance = dst_demean.T @ src_demean / num

    d = np.ones((dim,), dtype=np.float64)
    if np.linalg.det(covariance) < 0:
        d[dim - 1] = -1.0

    transform = np.eye(dim + 1, dtype=np.float64)

    U, S, Vt = np.linalg.svd(covariance)
    rank = np.linalg.matrix_rank(covariance)

    if rank == dim - 1:
        if np.linalg.det(U) * np.linalg.det(Vt) > 0:
            transform[:dim, :dim] = U @ Vt
        else:
            s = d[dim - 1]
            d[dim - 1] = -1.0
            transform[:dim, :dim] = U @ np.diag(d) @ Vt
            d[dim - 1] = s
    else:
        transform[:dim, :dim] = U @ np.diag(d) @ Vt

    scale = (S @ d) / src_demean.var(axis=0).sum()
    transform[:dim, dim] = dst_mean - scale * (transform[:dim, :dim] @ src_mean)
    transform[:dim, :dim] *= scale

    return transform[:dim, :]
