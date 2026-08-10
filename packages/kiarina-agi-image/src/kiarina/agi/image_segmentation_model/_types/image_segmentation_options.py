from typing import TypedDict

from .._models.image_segmentation_model import ImageSegmentationModel
from .image_segmentation_model_specifier import ImageSegmentationModelSpecifier


class ImageSegmentationOptions(TypedDict, total=False):
    image_segmentation_model: (
        ImageSegmentationModel | ImageSegmentationModelSpecifier | None
    )
