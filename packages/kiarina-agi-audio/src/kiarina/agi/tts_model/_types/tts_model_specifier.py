from typing import TypeAlias

from .tts_model_alias import TTSModelAlias
from .tts_model_name import TTSModelName

TTSModelSpecifier: TypeAlias = TTSModelName | TTSModelAlias | str
"""
A string in one of the following formats:

- {TTSModelName}
- {TTSModelName}?{ConfigString}
- {TTSModelAlias}
- {TTSModelAlias}?{ConfigString}

Examples:
- "gpt-4o-mini-tts"
- "gpt-4o-mini-tts?voice=alloy"
- "openai"
- "openai?voice=cedar"
"""
