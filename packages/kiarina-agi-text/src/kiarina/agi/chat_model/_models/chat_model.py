from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_provider import (
    ChatCapabilities,
    ChatProvider,
    ChatProviderName,
    chat_provider_registry,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice, ToolInfo

from .._schemas.chat_model_config import ChatModelConfig
from .._types.chat_model_name import ChatModelName


class ChatModel:
    def __init__(
        self,
        name: ChatModelName,
        config: ChatModelConfig,
    ) -> None:
        self.name: ChatModelName = name
        self.config: ChatModelConfig = config
        self._token_scale_factor: float | None = None
        self._provider: ChatProvider | None = None

    @property
    def provider_name(self) -> ChatProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def token_scale_factor(self) -> float:
        return self.config.token_scale_factor

    @property
    def provider(self) -> ChatProvider:
        if self._provider is None:
            self._provider = chat_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    def get_capabilities(self) -> ChatCapabilities:
        return self.provider.get_capabilities()

    async def run(
        self,
        messages: list[Message],
        *,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(
            chat_provider=str(self.provider),
            tool_infos=" | ".join(ti.name for ti in tool_infos) if tool_infos else None,
            tool_choice=tool_choice or "auto",
        )

        async for ai_message in self.provider.run(
            messages,
            tool_infos=tool_infos,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            yield ai_message

    def __str__(self) -> str:
        return self.name
