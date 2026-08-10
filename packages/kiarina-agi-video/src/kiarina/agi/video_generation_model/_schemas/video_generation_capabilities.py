from pydantic import BaseModel


class VideoGenerationCapabilities(BaseModel):
    edit_enabled: bool = False
    extend_enabled: bool = False
