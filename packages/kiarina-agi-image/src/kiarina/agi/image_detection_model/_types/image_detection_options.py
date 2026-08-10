from typing import TypedDict

from .._models.image_detection_model import ImageDetectionModel
from .image_detection_model_specifier import ImageDetectionModelSpecifier


class ImageDetectionOptions(TypedDict, total=False):
    image_detection_model: ImageDetectionModel | ImageDetectionModelSpecifier | None
