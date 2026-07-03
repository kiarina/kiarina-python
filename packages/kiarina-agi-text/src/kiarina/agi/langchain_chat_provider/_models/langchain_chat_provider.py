import json
import textwrap
import traceback
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatProviderContext,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk
from kiarina.agi.request_logger import (
    RequestLogEntry,
    RequestLogger,
    request_logger_registry,
)

from .._helpers.from_messages import from_messages
from .._helpers.from_tool_infos import from_tool_infos
from .._helpers.to_ai_message import to_ai_message
from .._helpers.to_ai_message_chunk import to_ai_message_chunk
from .._schemas.langchain_chat_provider_context import LangChainChatProviderContext
from .._types.lc_ai_message import LCAIMessage
from .._types.lc_ai_message_chunk import LCAIMessageChunk
from .._types.lc_message import LCMessage
from .._types.lc_tool_call import LCToolCall
from .._types.lc_tool_info import LCToolInfo
from .langchain_media_converter import LangChainMediaConverter


class LangChainChatProvider(BaseChatProvider, LangChainMediaConverter, ABC):
    @property
    def request_logger(self) -> RequestLogger:
        return request_logger_registry.resolve()

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        lc_ctx = LangChainChatProviderContext(
            lc_messages=await from_messages(
                ctx.messages,
                capabilities=ctx.capabilities,
                media_converter=self,
                run_context=ctx.run_context,
            ),
            lc_tool_infos=from_tool_infos(ctx.tool_infos) if ctx.tool_infos else None,
            tool_choice=ctx.tool_choice,
            parallel_tool_calls=ctx.parallel_tool_calls,
            cost_recorder=ctx.cost_recorder,
            run_context=ctx.run_context,
        )

        if ctx.streaming:
            async for ai_message in self._run_stream(lc_ctx):
                yield ai_message

        else:
            yield await self._run_invoke(lc_ctx)

    async def _run_invoke(self, ctx: LangChainChatProviderContext) -> AIMessage:
        chat_logger = chat_logger_registry.resolve()

        ctx = await self._pre_request(ctx)

        try:
            chat_logger.log_chat_invoke_start(ctx.run_context)

            try:
                lc_ai_message = await self._invoke(ctx)

            except Exception as e:
                if token_count := self._extract_overflow_token_count(e):
                    raise TokenOverflowError(token_count) from e
                else:
                    raise

            try:
                lc_ai_message = await self._post_request(ctx, lc_ai_message)
                ai_message = to_ai_message(lc_ai_message)
                chat_logger.log_chat_invoke_end(ai_message, ctx.run_context)

            finally:
                if cost_record := self._get_cost_record(lc_ai_message):
                    ctx.cost_recorder.add(cost_record)

            if self._is_safety_error(lc_ai_message):
                raise SafetyError()

            if self._is_max_token_error(lc_ai_message):
                raise MaxTokenError()

            await self._log_request_success(ctx, lc_ai_message)
            return ai_message

        except Exception as e:
            await self._error_request(ctx, e)
            await self._log_request_error(ctx, e)
            raise

        finally:
            await self._finalize_request(ctx)

    async def _run_stream(
        self, ctx: LangChainChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        chat_logger = chat_logger_registry.resolve()

        ctx = await self._pre_request(ctx)

        try:
            try:
                buffer: LCAIMessageChunk | None = None

                with chat_logger.log_chat_stream(ctx.run_context):
                    async for chunk in self._stream(ctx):
                        ai_message_chunk = to_ai_message_chunk(chunk)
                        chat_logger.log_chat_stream_chunk(ai_message_chunk)
                        yield ai_message_chunk

                        buffer = buffer + chunk if buffer else chunk

                if buffer is None:  # pragma: no cover
                    raise AssertionError("Empty stream response")

                lc_ai_message = LCAIMessage(
                    content=buffer.content,
                    additional_kwargs=buffer.additional_kwargs,
                    response_metadata=buffer.response_metadata,
                    name=buffer.name,
                    id=buffer.id,
                    tool_calls=buffer.tool_calls,
                    invalid_tool_calls=buffer.invalid_tool_calls,
                    usage_metadata=buffer.usage_metadata,
                )

            except Exception as e:
                if token_count := self._extract_overflow_token_count(e):
                    raise TokenOverflowError(token_count) from e
                else:
                    raise

            try:
                lc_ai_message = await self._post_request(ctx, lc_ai_message)
                ai_message = to_ai_message(lc_ai_message)

            finally:
                if cost_record := self._get_cost_record(lc_ai_message):
                    ctx.cost_recorder.add(cost_record)

            if self._is_safety_error(lc_ai_message):
                raise SafetyError()

            if self._is_max_token_error(lc_ai_message):
                raise MaxTokenError()

            await self._log_request_success(ctx, lc_ai_message)
            yield ai_message

        except Exception as e:
            await self._error_request(ctx, e)
            await self._log_request_error(ctx, e)
            raise

        finally:
            await self._finalize_request(ctx)

    # --------------------------------------------------
    # Template Methods (Lifecycle)
    # --------------------------------------------------

    async def _pre_request(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LangChainChatProviderContext:
        return ctx

    async def _post_request(
        self,
        ctx: LangChainChatProviderContext,
        lc_ai_message: LCAIMessage,
    ) -> LCAIMessage:
        return lc_ai_message

    async def _error_request(
        self,
        ctx: LangChainChatProviderContext,
        error: Exception,
    ) -> None:
        pass

    async def _finalize_request(
        self,
        ctx: LangChainChatProviderContext,
    ) -> None:
        pass

    # --------------------------------------------------
    # Template Methods (Invocation)
    # --------------------------------------------------

    @abstractmethod
    async def _invoke(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LCAIMessage: ...

    @abstractmethod
    async def _stream(
        self,
        ctx: LangChainChatProviderContext,
    ) -> AsyncIterator[LCAIMessageChunk]:
        yield LCAIMessageChunk(content="")  # pragma: no cover

    # --------------------------------------------------
    # Template Methods (Response Handling)
    # --------------------------------------------------

    @abstractmethod
    def _extract_overflow_token_count(self, error: Exception) -> int | None: ...

    @abstractmethod
    def _get_cost_record(self, lc_ai_message: LCAIMessage) -> CostRecord | None: ...

    @abstractmethod
    def _is_safety_error(self, lc_ai_message: LCAIMessage) -> bool: ...

    @abstractmethod
    def _is_max_token_error(self, lc_ai_message: LCAIMessage) -> bool: ...

    # --------------------------------------------------
    # Private Methods (Request Logging)
    # --------------------------------------------------

    async def _log_request_success(
        self,
        ctx: LangChainChatProviderContext,
        ai_message: LCAIMessage,
    ) -> None:
        await self.request_logger.log_request_success(
            _create_success_request_log_entry(ctx, ai_message, self.name),
            run_context=ctx.run_context,
        )

    async def _log_request_error(
        self,
        ctx: LangChainChatProviderContext,
        error: Exception,
    ) -> None:
        await self.request_logger.log_request_error(
            _create_error_request_log_entry(ctx, error, self.name),
            error=error,
            run_context=ctx.run_context,
        )


def _create_success_request_log_entry(
    ctx: LangChainChatProviderContext,
    ai_message: LCAIMessage,
    source: str,
) -> RequestLogEntry:
    metadata = {
        "kind": "langchain_chat_provider",
        "source": source,
        "status": "success",
        **ctx.run_context.model_dump(exclude={"metadata"}),
        **ctx.run_context.metadata,
        "message_count": len(ctx.lc_messages),
        "tool_infos": " | ".join(ti["name"] for ti in ctx.lc_tool_infos)
        if ctx.lc_tool_infos
        else "<none>",
        "tool_choice": ctx.tool_choice or "<none>",
        "tool_call": "yes" if ai_message.tool_calls else "no",
    }

    content = (
        f"{_format_tool_infos(ctx.lc_tool_infos) if ctx.lc_tool_infos else ''}\n\n"
        f"{_format_messages([*ctx.lc_messages, ai_message])}"
    ).strip()

    return RequestLogEntry(
        kind="langchain_chat_provider",
        source=source,
        content=content,
        metadata=metadata,
    )


def _create_error_request_log_entry(
    ctx: LangChainChatProviderContext,
    error: Exception,
    source: str,
) -> RequestLogEntry:
    metadata = {
        "kind": "langchain_chat_provider",
        "source": source,
        "status": "error",
        **ctx.run_context.model_dump(exclude={"metadata"}),
        **ctx.run_context.metadata,
        "message_count": len(ctx.lc_messages),
        "tool_infos": " | ".join(ti["name"] for ti in ctx.lc_tool_infos)
        if ctx.lc_tool_infos
        else "<none>",
        "tool_choice": ctx.tool_choice or "<none>",
        "error_type": type(error).__name__,
    }

    content = (
        f"{_format_error(error)}\n\n"
        f"{_format_tool_infos(ctx.lc_tool_infos) + '\n\n' if ctx.lc_tool_infos else ''}"
        f"{_format_messages(ctx.lc_messages)}"
    ).strip()

    return RequestLogEntry(
        kind="langchain_chat_provider",
        source=source,
        content=content,
        metadata=metadata,
    )


def _format_error(error: Exception) -> str:
    header = "## Error"
    content = f"{type(error).__name__}: {error}\n\n```\n{traceback.format_exc()}\n```"
    return f"{header}\n\n{content}".strip()


def _format_tool_infos(lc_tool_infos: list[LCToolInfo]) -> str:
    header = "## Tool Infos"
    content = "\n\n".join([_format_tool_info(ti) for ti in lc_tool_infos])
    return f"{header}\n\n{content}".strip()


def _format_tool_info(lc_tool_info: LCToolInfo) -> str:
    header = f"### {lc_tool_info['name']}"
    content = json.dumps(lc_tool_info, indent=2, ensure_ascii=False)
    return f"{header}\n\n```json\n{content}\n```".strip()


def _format_messages(lc_messages: list[LCMessage]) -> str:
    header = "## Messages"
    content = "\n\n".join([_format_message(m, i) for i, m in enumerate(lc_messages)])
    return f"{header}\n\n{content}".strip()


def _format_message(lc_message: LCMessage, offset: int) -> str:
    if isinstance(lc_message, LCAIMessage):
        return _format_ai_message(lc_message, offset)
    else:
        return _format_other_message(lc_message, offset)


def _format_ai_message(ai_message: LCAIMessage, offset: int) -> str:
    header = f"### [{offset}] {type(ai_message).__name__}"
    contents = _format_contents(ai_message.content)
    tool_calls = _format_tool_calls(ai_message.tool_calls)
    return f"{header}\n\n{contents}\n\n{tool_calls}".strip()


def _format_other_message(lc_message: LCMessage, offset: int) -> str:
    header = f"### [{offset}] {type(lc_message).__name__}"
    content = _format_contents(lc_message.content)
    return f"{header}\n\n{content}".strip()


def _format_contents(contents: str | list[str | dict[str, Any]]) -> str:
    if isinstance(contents, str):
        return _format_str(contents)

    texts: list[str] = []

    for i, content in enumerate(contents):
        texts.append(f"[{i}] " + _format_content(content))

    return "\n".join(texts)


def _format_content(content: str | dict[str, Any]) -> str:
    if isinstance(content, str):
        return _format_str(content)

    if content.get("type") == "text":
        return _format_str(str(content.get("text", "<None>")))

    if content.get("type") == "image":
        if "source" in content:
            return f"image source: {content['source']}"
        elif "mime_type" in content:
            return f"image mime_type: {content['mime_type']}"
        else:
            return "image"

    if content.get("type") == "image_url":
        if content["image_url"]["url"].startswith("data:"):
            return "image (data uri)"
        else:
            return f"image url: {content['image_url']['url']}"

    if content.get("type") == "media":
        return f"media mime_type: {content['mime_type']}"

    if content.get("type") == "input_file":
        return f"input_file (openai) filename: {content.get('filename', '<None>')}"

    if content.get("type") == "document":
        return f"document (anthropic) media_type: {content.get('source', {}).get('media_type', '<None>')}"

    return content.get("type") or "unknown"


def _format_str(s: str) -> str:
    return "text\n```\n" + textwrap.indent(s, prefix="> ") + "\n```"


def _format_tool_calls(tool_calls: list[LCToolCall]) -> str:
    texts: list[str] = []

    for i, tool_call in enumerate(tool_calls):
        texts.append(f"[{i}] " + _format_tool_call(tool_call))

    return "\n".join(texts)


def _format_tool_call(tool_call: LCToolCall) -> str:
    return f"tool_call\n```json\n{json.dumps(tool_call, indent=2, ensure_ascii=False)}\n```"
