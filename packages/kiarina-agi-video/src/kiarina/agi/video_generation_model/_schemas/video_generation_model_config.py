from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.video_generation_provider import VideoGenerationProviderName

from .video_generation_capabilities import VideoGenerationCapabilities


class VideoGenerationModelConfig(BaseModel):
    provider_name: VideoGenerationProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    capabilities: VideoGenerationCapabilities = Field(
        default_factory=VideoGenerationCapabilities
    )
