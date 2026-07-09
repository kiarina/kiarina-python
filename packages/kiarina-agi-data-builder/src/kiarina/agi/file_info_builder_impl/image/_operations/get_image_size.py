from io import BytesIO

from kiarina.agi.token_utils import ImageSize

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError(
        "Pillow is required to use ImageFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-image]'"
    ) from exc


def get_image_size(raw_data: bytes) -> ImageSize:
    image = Image.open(BytesIO(raw_data))
    width, height = image.size
    return ImageSize(width=width, height=height)
