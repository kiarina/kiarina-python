from typing import TypedDict

from .._models.audio_tagging_model import AudioTaggingModel
from .audio_tagging_model_specifier import AudioTaggingModelSpecifier


class AudioTaggingOptions(TypedDict, total=False):
    audio_tagging_model: AudioTaggingModel | AudioTaggingModelSpecifier | None
    top_k: int | None
    threshold: float | None
