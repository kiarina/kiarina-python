from typing import TypedDict

from kiarina.agi.tts_provider import OutputFormat

from .._models.tts_model import TTSModel
from .tts_model_specifier import TTSModelSpecifier


class TTSOptions(TypedDict, total=False):
    tts_model: TTSModel | TTSModelSpecifier | None
    instructions: str | None
    output_format: OutputFormat | None
    ignore_cache: bool | None
