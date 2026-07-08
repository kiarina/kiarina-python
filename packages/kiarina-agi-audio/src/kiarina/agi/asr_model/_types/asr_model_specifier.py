from typing import TypeAlias

from .asr_model_alias import ASRModelAlias
from .asr_model_name import ASRModelName

ASRModelSpecifier: TypeAlias = ASRModelName | ASRModelAlias | str
"""
A string in one of the following formats:

- {ASRModelName}
- {ASRModelName}?{ConfigString}
- {ASRModelAlias}
- {ASRModelAlias}?{ConfigString}

Examples:
- "gpt-4o-transcribe"
- "gpt-4o-transcribe?language=ja"
- "openai"
- "openai?temperature=0"
"""
