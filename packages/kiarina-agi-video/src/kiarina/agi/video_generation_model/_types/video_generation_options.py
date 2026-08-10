from typing import TypedDict

from .._models.video_generation_model import VideoGenerationModel
from .video_generation_model_specifier import VideoGenerationModelSpecifier


class VideoGenerationOptions(TypedDict, total=False):
    video_generation_model: VideoGenerationModel | VideoGenerationModelSpecifier | None
