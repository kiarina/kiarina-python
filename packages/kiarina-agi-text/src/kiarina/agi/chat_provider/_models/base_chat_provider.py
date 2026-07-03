import json
import textwrap
import traceback
from collections.abc import AsyncIterator

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, Message
from kiarina.agi.request_logger import RequestLogEntry, request_logger_registry
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice, ToolInfo

from .._schemas.chat_capabilities import ChatCapabilities
from .._schemas.chat_provider_context import ChatProviderContext
from .._types.chat_provider import ChatProvider
from .._types.chat_provider_name import ChatProviderName


class BaseChatProvider(ChatProvider):
    def __init__(self) -> None:
        self._name: ChatProviderName | None = None

    @property
    def name(self) -> ChatProviderName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Chat provider name not set")

        return self._name

    @name.setter
    def name(self, value: ChatProviderName) -> None:
        self._name = value

    def __str__(self) -> str:
        return self.__class__.__name__

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities()

    async def run(
        self,
        messages: list[Message],
        *,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        ctx = ChatProviderContext(
            messages=messages,
            tool_infos=tool_infos,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            streaming=streaming,
            capabilities=self.get_capabilities(),
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        try:
            async for ai_message in self._run(ctx):
                yield ai_message

                if ai_message.type == "ai":
                    await request_logger_registry.resolve().log_request_success(
                        _create_success_request_log_entry(ctx, ai_message, self.name),
                        run_context=ctx.run_context,
                    )

        except Exception as e:
            await request_logger_registry.resolve().log_request_error(
                _create_error_request_log_entry(ctx, e, self.name),
                error=e,
                run_context=ctx.run_context,
            )
            raise

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if False:
            yield


def _create_success_request_log_entry(
    ctx: ChatProviderContext,
    ai_message: AIMessage,
    chat_provider_name: ChatProviderName,
) -> RequestLogEntry:
    metadata = {
        "kind": "chat_model",
        "source": chat_provider_name,
        "status": "success",
        **ctx.run_context.model_dump(exclude={"metadata"}),
        **ctx.run_context.metadata,
        "message_count": len(ctx.messages),
        "tool_infos": " | ".join(ti.name for ti in ctx.tool_infos)
        if ctx.tool_infos
        else "<none>",
        "tool_choice": ctx.tool_choice or "<none>",
        "tool_call": "yes" if ai_message.tool_calls else "no",
    }

    content = (
        f"{_format_tool_infos(ctx.tool_infos) if ctx.tool_infos else ''}\n\n"
        f"{_format_messages([*ctx.messages, ai_message])}"
    ).strip()

    return RequestLogEntry(
        kind="chat_provider",
        source=chat_provider_name,
        content=content,
        metadata=metadata,
    )


def _create_error_request_log_entry(
    ctx: ChatProviderContext,
    error: Exception,
    chat_provider_name: ChatProviderName,
) -> RequestLogEntry:
    metadata = {
        "kind": "chat_model",
        "source": chat_provider_name,
        "status": "error",
        **ctx.run_context.model_dump(exclude={"metadata"}),
        **ctx.run_context.metadata,
        "message_count": len(ctx.messages),
        "tool_infos": " | ".join(ti.name for ti in ctx.tool_infos)
        if ctx.tool_infos
        else "<none>",
        "tool_choice": ctx.tool_choice or "<none>",
        "error_type": type(error).__name__,
    }

    content = (
        f"{_format_error(error)}\n\n"
        f"{_format_tool_infos(ctx.tool_infos) + '\n\n' if ctx.tool_infos else ''}"
        f"{_format_messages(ctx.messages)}"
    ).strip()

    return RequestLogEntry(
        kind="chat_provider",
        source=chat_provider_name,
        content=content,
        metadata=metadata,
    )


def _format_tool_infos(tool_infos: list[ToolInfo]) -> str:
    header = "## Tool Infos"
    content = "\n\n".join([_format_tool_info(ti) for ti in tool_infos])
    return f"{header}\n\n{content}".strip()


def _format_tool_info(tool_info: ToolInfo) -> str:
    header = f"### {tool_info.name}"
    json_schema = tool_info.to_json_schema()

    if tool_info.cache_control:
        json_schema["cache_control"] = tool_info.cache_control

    content = json.dumps(json_schema, indent=2, ensure_ascii=False)
    return f"{header}\n\n```json\n{content}\n```".strip()


def _format_messages(messages: list[Message]) -> str:
    header = "## Messages"
    content = "\n\n".join([_format_message(m, i) for i, m in enumerate(messages)])
    return f"{header}\n\n{content}".strip()


def _format_message(message: Message, offset: int) -> str:
    header = f"### [{offset}] {type(message).__name__}"
    content = "text\n```\n" + textwrap.indent(message.to_text(), prefix="> ") + "\n```"
    return f"{header}\n\n{content}".strip()


def _format_error(error: Exception) -> str:
    header = "## Error"
    content = f"{type(error).__name__}: {error}\n\n```\n{traceback.format_exc()}```"
    return f"{header}\n\n{content}".strip()
