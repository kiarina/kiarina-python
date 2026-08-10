import numpy as np

from kiarina.agi.image_types import ImagePixels


def ensure_image_pixels(pixels: object) -> ImagePixels:
    array = np.asarray(pixels)

    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(
            "VideoSource expects pixels shaped as [height, width, 3] (RGB), "
            f"got shape {array.shape}."
        )

    if array.dtype != np.uint8:
        raise ValueError(f"VideoSource expects uint8 pixels, got dtype {array.dtype}.")

    return array
