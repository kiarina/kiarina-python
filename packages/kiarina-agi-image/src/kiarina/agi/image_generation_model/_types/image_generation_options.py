from typing import TypedDict

from .._models.image_generation_model import ImageGenerationModel
from .image_generation_model_specifier import ImageGenerationModelSpecifier


class ImageGenerationOptions(TypedDict, total=False):
    image_generation_model: ImageGenerationModel | ImageGenerationModelSpecifier | None
