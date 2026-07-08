from typing import TypedDict

from .._models.asr_model import ASRModel
from .asr_model_specifier import ASRModelSpecifier


class ASROptions(TypedDict, total=False):
    asr_model: ASRModel | ASRModelSpecifier | None
