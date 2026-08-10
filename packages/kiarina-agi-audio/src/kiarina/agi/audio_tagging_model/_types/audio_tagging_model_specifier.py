from typing import TypeAlias

from .audio_tagging_model_alias import AudioTaggingModelAlias
from .audio_tagging_model_name import AudioTaggingModelName

AudioTaggingModelSpecifier: TypeAlias = (
    AudioTaggingModelName | AudioTaggingModelAlias | str
)
"""
A string in one of the following formats:

- {AudioTaggingModelName}
- {AudioTaggingModelName}?{ConfigString}
- {AudioTaggingModelAlias}
- {AudioTaggingModelAlias}?{ConfigString}
"""
