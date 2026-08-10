import math

from .._types.image_size import ImageSize
from .._types.token_count import TokenCount

_BASE_TOKENS = 70  # gpt-5
_TILE_TOKENS = 140  # gpt-5
_MAX_DIMENSION = 2048
_TARGET_MIN_SIDE = 768
_TILE_SIZE = 512


def calc_image_token(image_size: ImageSize) -> TokenCount:
    # NOTE: https://developers.openai.com/api/docs/guides/images-vision
    width, height = image_size.width, image_size.height

    scale_factor = min(_MAX_DIMENSION / width, _MAX_DIMENSION / height)

    if scale_factor < 1:
        width = int(width * scale_factor)
        height = int(height * scale_factor)

    min_side = min(width, height)

    if min_side > _TARGET_MIN_SIDE:
        scale_factor = _TARGET_MIN_SIDE / min_side
        width = int(width * scale_factor)
        height = int(height * scale_factor)

    total_tiles = math.ceil(width / _TILE_SIZE) * math.ceil(height / _TILE_SIZE)
    return _BASE_TOKENS + (total_tiles * _TILE_TOKENS)
