import asyncio
import os
from io import BytesIO
from typing import TypeAlias, cast

import kiarina.utils.file as kf

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError(
        "Pillow is required to use ImageFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-image]'"
    ) from exc

OutputFilePath: TypeAlias = str

MAX_SIZE = 2048


async def build_intermediate_image(
    input_file_path: str, output_base_path: str
) -> OutputFilePath | None:
    return await asyncio.to_thread(
        _build_intermediate_image, input_file_path, output_base_path
    )


def _build_intermediate_image(
    input_file_path: str, output_base_path: str
) -> OutputFilePath | None:
    image = _get_image(input_file_path)

    transparency = _has_transparency(image)

    if not _should_resize(image) and not _should_convert_to_jpeg(image, transparency):
        return None

    if transparency:
        output_file_path = f"{output_base_path}.png"
    else:
        output_file_path = f"{output_base_path}.jpg"

    if os.path.exists(output_file_path):
        return output_file_path

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    if _should_resize(image):
        image = _resize_image(image)
    else:
        image = image.copy()

    if _should_convert_to_jpeg(image, transparency):
        image = _flatten_transparency_to_rgb(image)
        image.save(output_file_path, "JPEG", quality=85, optimize=True)
    else:
        image.save(output_file_path, "PNG", optimize=True)

    return output_file_path


def _get_image(input_file_path: str) -> Image.Image:
    file_blob = kf.read_file(input_file_path)

    if not file_blob:
        raise FileNotFoundError(f"File not found: {input_file_path}")

    return Image.open(BytesIO(file_blob.raw_data))


def _has_transparency(image: Image.Image) -> bool:
    if image.mode not in ("RGBA", "LA", "P"):
        return False

    if image.mode in ("RGBA", "LA"):
        alpha_channel = image.split()[-1]
        extrema = alpha_channel.getextrema()

        if isinstance(extrema, tuple) and len(extrema) == 2:
            min_alpha = extrema[0]

            if isinstance(min_alpha, (int, float)):
                return min_alpha < 255

        return False

    elif image.mode == "P":
        if "transparency" not in image.info:
            return False

        transparent_index = image.info["transparency"]
        histogram = image.histogram()
        return cast(bool, histogram[transparent_index] > 0)

    return False


def _should_resize(image: Image.Image) -> bool:
    width, height = image.size
    return width > MAX_SIZE or height > MAX_SIZE


def _should_convert_to_jpeg(image: Image.Image, transparency: bool) -> bool:
    return image.format != "JPEG" and not transparency


def _resize_image(image: Image.Image) -> Image.Image:
    width, height = image.size
    scale_factor = min(MAX_SIZE / width, MAX_SIZE / height)
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def _flatten_transparency_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA", "P"):
        rgb_image = Image.new("RGB", image.size, (255, 255, 255))

        if image.mode == "P":
            image = image.convert("RGBA")

        rgb_image.paste(
            image,
            mask=(image.split()[-1] if image.mode in ("RGBA", "LA") else None),
        )

        return rgb_image

    return image
