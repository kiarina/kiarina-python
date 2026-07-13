import asyncio
from io import BytesIO
from typing import Literal

import numpy as np
from PIL import Image

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.utils.mime import MIMEBlob

from .._types.image_segmentation_options import ImageSegmentationOptions
from .segment_image import segment_image


async def remove_background(
    file_path: str,
    *,
    output_format: Literal["png", "webp"] = "png",
    image_segmentation_options: ImageSegmentationOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> MIMEBlob:
    if output_format == "png":
        mime_type = "image/png"
    elif output_format == "webp":
        mime_type = "image/webp"
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    pixels = await asyncio.to_thread(_load_pixels, file_path)
    segmentation = await segment_image(
        pixels,
        image_segmentation_options=image_segmentation_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
    raw_data = await asyncio.to_thread(
        _encode_image,
        pixels,
        segmentation.mask,
        output_format,
    )
    return MIMEBlob(mime_type=mime_type, raw_data=raw_data)


def _load_pixels(file_path: str) -> np.ndarray:
    with Image.open(file_path) as image:
        return np.array(image.convert("RGB"), dtype=np.uint8)


def _encode_image(
    pixels: np.ndarray,
    mask: np.ndarray,
    output_format: Literal["png", "webp"],
) -> bytes:
    rgba = np.concatenate((pixels, mask[..., np.newaxis]), axis=2)
    output = BytesIO()
    Image.fromarray(rgba).save(output, format=output_format.upper())
    return output.getvalue()
