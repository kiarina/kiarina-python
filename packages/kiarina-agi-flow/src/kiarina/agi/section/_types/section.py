from collections.abc import AsyncIterator
from typing import Protocol

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.event import Event
from kiarina.agi.message import Message
from kiarina.agi.token_utils import TokenCount
from kiarina.agi.tool_info import ToolInfo

from .._schemas.section_context import SectionContext
from .weight import Weight


class Section(Protocol):
    weight: Weight

    ctx: SectionContext

    def prepare(self) -> AsyncIterator[Event]: ...

    def get_system_texts(self) -> list[str]: ...

    def get_messages(self) -> list[Message]: ...

    def get_tool_infos(self) -> list[ToolInfo]: ...

    def is_resizable(self) -> bool: ...

    def resize(self, reduce: TokenCount) -> AsyncIterator[Event]: ...

    def ready(self) -> AsyncIterator[Event]: ...

    def get_estimates(self, ignore_cache: bool = False) -> ChatEstimates: ...
