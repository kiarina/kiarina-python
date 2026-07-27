from io import BytesIO

import numpy as np
from PIL import Image

from kiarina.agi.file_info_builder_impl.video._utils.encode_video_frame_jpeg import (
    encode_video_frame_jpeg,
)


def test_encode_video_frame_jpeg() -> None:
    pixels = np.zeros((4, 6, 3), dtype=np.uint8)
    raw_data = encode_video_frame_jpeg(pixels)

    image = Image.open(BytesIO(raw_data))
    assert image.format == "JPEG"
    assert image.size == (6, 4)
