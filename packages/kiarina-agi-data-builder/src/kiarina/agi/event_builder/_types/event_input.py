from typing import Any, Literal, TypeAlias

from kiarina.agi.event import Event
from kiarina.agi.message_builder import MessageInput

EventInput: TypeAlias = MessageInput | tuple[Literal["custom"], dict[str, Any]] | Event
