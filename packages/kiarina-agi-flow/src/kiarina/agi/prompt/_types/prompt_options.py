from typing import TypedDict

from kiarina.agi.chat_limits import ChatLimits, ChatLimitsSpecifier

from .prompt import Prompt
from .prompt_specifier import PromptSpecifier


class PromptOptions(TypedDict, total=False):
    prompt: Prompt | PromptSpecifier | None
    limits: ChatLimits | ChatLimitsSpecifier | None
