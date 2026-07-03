from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice, ToolInfo

from .._schemas.chat_capabilities import ChatCapabilities
from .chat_provider_name import ChatProviderName


@runtime_checkable
class ChatProvider(Protocol):
    """
    Chat Provider

    Raises:
        MaxTokenError: If the request exceeds the model's maximum token limit.
        SafetyError: If the model determines the content is unsafe.
        TokenOverflowError: If the response exceeds the model's maximum token limit.
    """

    name: ChatProviderName

    def get_capabilities(self) -> ChatCapabilities: ...

    def run(
        self,
        messages: list[Message],
        *,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> AsyncIterator[AIMessageChunk | AIMessage]: ...
