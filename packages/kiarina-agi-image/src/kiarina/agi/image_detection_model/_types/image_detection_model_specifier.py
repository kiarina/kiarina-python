from typing import TypeAlias

from .image_detection_model_alias import ImageDetectionModelAlias
from .image_detection_model_name import ImageDetectionModelName

ImageDetectionModelSpecifier: TypeAlias = (
    ImageDetectionModelName | ImageDetectionModelAlias | str
)
"""
A string in one of the following formats:

- {ImageDetectionModelName}
- {ImageDetectionModelName}?{ConfigString}
- {ImageDetectionModelAlias}
- {ImageDetectionModelAlias}?{ConfigString}
"""
