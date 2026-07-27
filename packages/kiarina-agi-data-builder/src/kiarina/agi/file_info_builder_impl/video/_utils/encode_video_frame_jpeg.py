from io import BytesIO

from kiarina.agi.image_types import ImagePixels

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError(
        "Pillow is required to build video analysis frame bundles. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-video]'"
    ) from exc


def encode_video_frame_jpeg(pixels: ImagePixels) -> bytes:
    buffer = BytesIO()
    Image.fromarray(pixels).save(buffer, format="JPEG", quality=85, optimize=True)
    return buffer.getvalue()
