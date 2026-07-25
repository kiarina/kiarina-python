from typing import TypeAlias

from .chat_model_alias import ChatModelAlias
from .chat_model_name import ChatModelName

ChatModelSpecifier: TypeAlias = ChatModelName | ChatModelAlias | str
"""
A string in one of the following formats:

- {ChatModelName}
- {ChatModelName}?{ConfigString}
- {ChatModelAlias}
- {ChatModelAlias}?{ConfigString}

Examples:
- "gpt-5.6-sol"
- "gpt-5.6-sol?reasoning_effort=high"
- "openai"
- "openai?reasoning_effort=high"
"""
