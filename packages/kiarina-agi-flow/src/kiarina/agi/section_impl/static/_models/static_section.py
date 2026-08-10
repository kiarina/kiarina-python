from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.message import Message
from kiarina.agi.section import BaseSection
from kiarina.agi.tool_info import ToolInfo


class StaticSection(BaseSection):
    def __init__(
        self,
        *,
        system_texts: list[str] | None = None,
        messages: list[Message] | None = None,
        tool_infos: list[ToolInfo] | None = None,
        ready_event: Event | dict[str, Any] | None = None,
    ) -> None:
        super().__init__()

        self.fixed_system_texts: list[str] = system_texts or []
        self.fixed_messages: list[Message] = messages or []
        self.fixed_tool_infos: list[ToolInfo] = tool_infos or []
        self.ready_event: Event | dict[str, Any] | None = ready_event

    def get_system_texts(self) -> list[str]:
        return self.fixed_system_texts

    def get_messages(self) -> list[Message]:
        return self.fixed_messages

    def get_tool_infos(self) -> list[ToolInfo]:
        return self.fixed_tool_infos

    async def ready(self) -> AsyncIterator[Event]:
        if self.ready_event is None:
            return

        if isinstance(self.ready_event, dict):
            yield CustomEvent(payload=self.ready_event)
            return

        yield self.ready_event
