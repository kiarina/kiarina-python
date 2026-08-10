import asyncio
import json
import logging
from collections.abc import AsyncIterator

from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.message import (
    AIMessage,
    AIMessageChunk,
    Message,
    ToolCall,
    ToolCallChunk,
)
from kiarina.agi.tool_info import ToolInfo

from .._settings import MockChatProviderSettings

try:
    import ulid
except ImportError as exc:
    raise ImportError(
        "ulid-py is required to use MockChatProvider. "
        "Install it with: pip install 'kiarina-agi-text[chat-provider-mock]'"
    ) from exc

logger = logging.getLogger(__name__)


class MockChatProvider(BaseChatProvider):
    """
    Mock Chat Provider Implementation for Testing
    """

    def __init__(self, settings: MockChatProviderSettings) -> None:
        super().__init__()

        self.settings: MockChatProviderSettings = settings

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities.model_validate(self.settings.model_dump())

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if ctx.streaming:
            async for ai_message in self._stream(ctx):
                yield ai_message
        else:
            yield await self._invoke(ctx)

    async def _invoke(self, ctx: ChatProviderContext) -> AIMessage:
        chat_logger = chat_logger_registry.resolve()
        chat_logger.log_chat_invoke_start(ctx.run_context)

        check_error_simulation(ctx.messages)
        content, tool_calls = generate_result(ctx.messages, ctx.tool_infos)

        if self.settings.simulate_delay:
            await asyncio.sleep(self.settings.delay_seconds)

        ai_message = AIMessage.create(text=content, tool_calls=tool_calls)
        chat_logger.log_chat_invoke_end(ai_message, ctx.run_context)
        return ai_message

    async def _stream(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        chat_logger = chat_logger_registry.resolve()

        with chat_logger.log_chat_stream(ctx.run_context):
            check_error_simulation(ctx.messages)
            content, tool_calls = generate_result(ctx.messages, ctx.tool_infos)

            if content:
                chunk_size = self.settings.stream_chunk_size

                for i in range(0, len(content), chunk_size):
                    chunk_content = content[i : i + chunk_size]

                    if self.settings.simulate_delay:
                        await asyncio.sleep(self.settings.stream_delay_seconds)

                    ai_message_chunk = AIMessageChunk.create(text=chunk_content)
                    chat_logger.log_chat_stream_chunk(ai_message_chunk)
                    yield ai_message_chunk

            if tool_calls:
                for tool_call in tool_calls:
                    ai_message_chunk = AIMessageChunk(
                        tool_call_chunks=[
                            ToolCallChunk(
                                id=tool_call.id,
                                name=tool_call.name,
                                args=json.dumps(tool_call.args),
                                index=0,
                            )
                        ],
                    )
                    chat_logger.log_chat_stream_chunk(ai_message_chunk)
                    yield ai_message_chunk

            ai_message = AIMessage.create(text=content, tool_calls=tool_calls)

        yield ai_message


def check_error_simulation(messages: list[Message]) -> None:
    if not messages:  # pragma: no cover
        return

    last_message = messages[-1]

    try:
        info = json.loads(last_message.to_text())
    except (json.JSONDecodeError, KeyError):
        return

    if not isinstance(info, dict):  # pragma: no cover
        return

    if info.get("type") == "token_overflow_error":
        token_count = info.get("token_count", 100_000)
        raise TokenOverflowError(token_count)

    elif info.get("type") == "safety_error":
        raise SafetyError("Mock safety error")

    elif info.get("type") == "max_token_error":
        raise MaxTokenError("Mock max token error")

    elif info.get("type") == "unknown_error":
        raise RuntimeError("Mock unknown error")


def generate_result(
    messages: list[Message],
    tool_infos: list[ToolInfo] | None = None,
) -> tuple[str, list[ToolCall]]:
    if not messages:  # pragma: no cover
        return "", []

    last_message = messages[-1]

    default_content = f"Response to: {last_message.to_text()[:50]}"

    try:
        info = json.loads(last_message.to_text())
    except json.JSONDecodeError:
        return default_content, []

    if not isinstance(info, dict):  # pragma: no cover
        return default_content, []

    content = info.get("content", "")

    tool_calls: list[ToolCall] = []

    for item in info.get("tool_calls", []):
        if isinstance(item, dict):
            tool_calls.append(
                ToolCall(
                    id=item.get("id", ulid.new().str),
                    name=item.get("name", "unknown_tool"),
                    args=item.get("args", {}),
                )
            )

    check_tool_calls(tool_calls, tool_infos)

    if not content and not tool_calls:  # pragma: no cover
        return default_content, []

    return content, tool_calls


def check_tool_calls(
    tool_calls: list[ToolCall],
    tool_infos: list[ToolInfo] | None,
) -> None:
    if not tool_calls:
        return

    available_tool_names = {tool_info.name for tool_info in tool_infos or []}

    for tool_call in tool_calls:
        if tool_call.name not in available_tool_names:
            raise ValueError(
                f"Mock tool call requested unavailable tool: {tool_call.name}"
            )
