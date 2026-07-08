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
- "sora-2"
- "sora-2?resolution=720p"
- "openai"
- "openai?duration_seconds=10"
"""
