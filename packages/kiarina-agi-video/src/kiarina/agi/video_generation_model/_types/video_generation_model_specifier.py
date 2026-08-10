from typing import TypeAlias

from .video_generation_model_alias import VideoGenerationModelAlias
from .video_generation_model_name import VideoGenerationModelName

VideoGenerationModelSpecifier: TypeAlias = (
    VideoGenerationModelName | VideoGenerationModelAlias | str
)
"""
A string in one of the following formats:

- {VideoGenerationModelName}
- {VideoGenerationModelName}?{ConfigString}
- {VideoGenerationModelAlias}
- {VideoGenerationModelAlias}?{ConfigString}

Examples:
- "veo-3.1"
- "veo-3.1?resolution=720p"
- "google"
- "google?duration_seconds=8"
"""
