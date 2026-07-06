from typing import TypeAlias

from .image_generation_model_alias import ImageGenerationModelAlias
from .image_generation_model_name import ImageGenerationModelName

ImageGenerationModelSpecifier: TypeAlias = (
    ImageGenerationModelName | ImageGenerationModelAlias | str
)
"""
A string in one of the following formats:

- {ImageGenerationModelName}
- {ImageGenerationModelName}?{ConfigString}
- {ImageGenerationModelAlias}
- {ImageGenerationModelAlias}?{ConfigString}

Examples:
- "gpt-image-1.5"
- "gpt-image-1.5?size=1024x1024"
- "openai"
- "openai?background=transparent"
"""
