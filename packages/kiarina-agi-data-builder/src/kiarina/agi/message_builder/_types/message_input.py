from typing import Any, Literal, TypeAlias

from kiarina.agi.message import Message

from .ai_message_spec import AIMessageSpec
from .human_message_spec import HumanMessageSpec
from .tool_message_spec import ToolMessageSpec

MessageInput: TypeAlias = (
    str
    | HumanMessageSpec
    | tuple[Literal["human"], str | dict[str, Any] | HumanMessageSpec]
    | tuple[Literal["ai"], str | dict[str, Any] | AIMessageSpec]
    | tuple[Literal["tool"], dict[str, Any] | ToolMessageSpec]
    | Message
)
