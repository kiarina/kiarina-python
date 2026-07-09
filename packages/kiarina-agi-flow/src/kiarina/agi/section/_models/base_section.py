from collections.abc import AsyncIterator

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.event import Event
from kiarina.agi.message import Message
from kiarina.agi.token_utils import TokenCount, calc_text_token
from kiarina.agi.tool_info import ToolInfo

from .._schemas.section_context import SectionContext
from .._types.section import Section
from .._types.weight import Weight


class BaseSection(Section):
    def __init__(self) -> None:
        self.weight: Weight = 1.0
        self._ctx: SectionContext | None = None
        self._estimates: ChatEstimates | None = None

    @property
    def ctx(self) -> SectionContext:
        if self._ctx is None:
            raise ValueError("Section context is not set")

        return self._ctx

    @ctx.setter
    def ctx(self, value: SectionContext) -> None:
        self._ctx = value

    async def prepare(self) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield

    def get_system_texts(self) -> list[str]:
        return []

    def get_messages(self) -> list[Message]:
        return []

    def get_tool_infos(self) -> list[ToolInfo]:
        return []

    def is_resizable(self) -> bool:
        return False

    async def resize(self, reduce: TokenCount) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield

    async def ready(self) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield

    def get_estimates(self, ignore_cache: bool = False) -> ChatEstimates:
        if self._estimates and not ignore_cache:
            return self._estimates

        self._estimates = self._to_estimates()
        return self._estimates

    def _to_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()

        for text in self.get_system_texts():
            estimates.add_token_count("text", calc_text_token(text))

        for message in self.get_messages():
            estimates += message.to_estimates()

        for tool_info in self.get_tool_infos():
            estimates += tool_info.to_estimates()

        return estimates

    def _to_string(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"{'[' + str(self.weight) + ']' if self.weight != 1.0 else ''}"
            f"{'(' + str(self._estimates.token_count) + ' tokens)' if self._estimates is not None else ''}"
        )

    def __str__(self) -> str:
        return self._to_string()
