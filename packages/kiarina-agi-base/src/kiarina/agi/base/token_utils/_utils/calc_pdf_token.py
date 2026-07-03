from .._helpers.calc_text_token import calc_text_token
from .._types.image_size import ImageSize
from .calc_image_token import calc_image_token


def calc_pdf_token(text: str, image_sizes: list[ImageSize]) -> int:
    return calc_text_token(text) + sum(calc_image_token(i) for i in image_sizes)
