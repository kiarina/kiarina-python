import asyncio
import math
import os
import re
import tempfile
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter, to_transcript
from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.content import Content
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCallChunk
from kiarina.utils.mime import MIMEBlob

from .._constants.tool_name_prefix import MCP_SERVER_NAME, TOOL_NAME_PREFIX
from .._operations.create_child_env import create_child_env
from .._operations.from_claude_agent_sdk_messages import (
    from_claude_agent_sdk_messages,
)
from .._operations.to_sdk_mcp_tools import to_sdk_mcp_tools
from .._schemas.claude_agent_sdk_chat_result import ClaudeAgentSDKChatResult
from .._settings import ClaudeAgentSDKChatProviderSettings

try:
    import claude_agent_sdk
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultError,
        ResultMessage,
        StreamEvent,
    )
except ImportError as exc:
    raise ImportError(
        "claude-agent-sdk is required to use ClaudeAgentSDKChatProvider. "
        "Install it with: pip install 'kiarina-agi-text[chat-provider-claude-agent-sdk]'"
    ) from exc

_SESSION_NAME = "kiarina-agi-text"
"""Naming the session stops Claude Code from sending the prompt again to name it."""


class ClaudeAgentSDKChatProvider(BaseChatProvider, MediaConverter):
    """
    Claude Agent SDK Chat Provider Implementation

    Runs Claude Code with its own login, one new session per request. The
    conversation is sent as one `<messages>` XML prompt, Claude Code's own tools
    and settings are turned off, and the run stops after the first model turn
    (`max_turns=1`), so the caller runs the tool calls.
    """

    def __init__(self, settings: ClaudeAgentSDKChatProviderSettings) -> None:
        super().__init__()

        self.settings: ClaudeAgentSDKChatProviderSettings = settings

    def __str__(self) -> str:
        props: list[str] = [self.settings.model_name]

        if self.settings.effort:
            props.append(self.settings.effort)

        return f"{self.__class__.__name__}({', '.join(props)})"

    # --------------------------------------------------
    # Methods (ChatProvider)
    # --------------------------------------------------

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities.model_validate(self.settings.model_dump())

    # --------------------------------------------------
    # Methods (MediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_blob.mime_type,
                "data": mime_blob.raw_base64_str,
            },
        }

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> ContentPart | None:
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": mime_blob.raw_base64_str,
            },
        }

    # --------------------------------------------------
    # Methods (BaseChatProvider)
    # --------------------------------------------------

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        transcript = await to_transcript(
            ctx.messages,
            capabilities=ctx.capabilities,
            media_converter=self,
            run_context=ctx.run_context,
        )
        tool_infos = ctx.tool_infos or []
        system_prompt = transcript.to_system_prompt(tools_enabled=bool(tool_infos))
        user_prompt = transcript.to_user_prompt(
            tool_choice=ctx.tool_choice if tool_infos else None
        )
        user_content: list[ContentPart] = [
            {"type": "text", "text": user_prompt},
            *transcript.media_parts,
        ]

        parallel_tool_calls = ctx.parallel_tool_calls

        if parallel_tool_calls is None:
            parallel_tool_calls = self.settings.parallel_tool_calls is not False

        chat_logger = chat_logger_registry.resolve()

        with tempfile.TemporaryDirectory(prefix="kiarina-claude-agent-sdk-") as cwd:
            options = self.create_options(
                system_prompt=system_prompt,
                tool_infos=tool_infos,
                streaming=bool(ctx.streaming),
                cwd=cwd,
            )

            if ctx.streaming:
                with chat_logger.log_chat_stream(ctx.run_context):
                    async for item in self._query(
                        user_content, options, parallel_tool_calls
                    ):
                        if isinstance(item, AIMessageChunk):
                            chat_logger.log_chat_stream_chunk(item)
                            yield item
                        else:
                            yield self._handle_result(ctx, item)
            else:
                chat_logger.log_chat_invoke_start(ctx.run_context)

                async for item in self._query(
                    user_content, options, parallel_tool_calls
                ):
                    if isinstance(item, ClaudeAgentSDKChatResult):
                        ai_message = self._handle_result(ctx, item)
                        chat_logger.log_chat_invoke_end(ai_message, ctx.run_context)
                        yield ai_message

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def create_options(
        self,
        *,
        system_prompt: str,
        tool_infos: list[Any],
        streaming: bool,
        cwd: str,
    ) -> ClaudeAgentOptions:
        mcp_servers: dict[str, Any] = {}
        allowed_tools: list[str] = []

        if tool_infos:
            mcp_servers[MCP_SERVER_NAME] = claude_agent_sdk.create_sdk_mcp_server(
                name=MCP_SERVER_NAME, version="1", tools=to_sdk_mcp_tools(tool_infos)
            )
            allowed_tools = [f"{TOOL_NAME_PREFIX}{t.name}" for t in tool_infos]

        return ClaudeAgentOptions(
            model=self.settings.model_name,
            effort=self.settings.effort,
            system_prompt=system_prompt,
            tools=[],
            mcp_servers=mcp_servers,
            strict_mcp_config=True,
            setting_sources=[],
            allowed_tools=allowed_tools,
            permission_mode="bypassPermissions",
            max_turns=1,
            cwd=cwd,
            cli_path=self.settings.cli_path,
            env=create_child_env(os.environ, self.settings.env),
            extra_args={"no-session-persistence": None, "name": _SESSION_NAME},
            include_partial_messages=streaming,
        )

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    async def _query(
        self,
        user_content: list[ContentPart],
        options: ClaudeAgentOptions,
        parallel_tool_calls: bool,
    ) -> AsyncIterator[AIMessageChunk | ClaudeAgentSDKChatResult]:
        content_blocks: list[Any] = []
        result_message: ResultMessage | None = None

        async def prompt() -> AsyncIterator[dict[str, Any]]:
            yield {
                "type": "user",
                "message": {"role": "user", "content": user_content},
                "parent_tool_use_id": None,
            }

        error: ResultError | None = None

        try:
            async with asyncio.timeout(self.settings.timeout):
                async for message in claude_agent_sdk.query(
                    prompt=prompt(), options=options
                ):
                    if isinstance(message, StreamEvent):
                        if chunk := _to_ai_message_chunk(message.event):
                            yield chunk
                    elif isinstance(message, AssistantMessage):
                        content_blocks.extend(message.content)
                    elif isinstance(message, ResultMessage):
                        result_message = message
        except ResultError as e:
            # NOTE: The SDK raises after an error result. Reaching `max_turns` after
            # a tool call is one, and is how every tool-calling request ends.
            if result_message is None:
                raise

            error = e

        if result_message is None:
            raise RuntimeError("Claude Code ended without a result.")

        if result_message.is_error and not _is_turn_limit(result_message):
            message_text = str(result_message.result or result_message.errors or error)

            if token_count := _extract_overflow_token_count(message_text):
                raise TokenOverflowError(token_count) from error

            raise RuntimeError(
                f"Claude Code failed ({result_message.subtype}): {message_text}"
            ) from error

        yield from_claude_agent_sdk_messages(
            content_blocks, result_message, parallel_tool_calls=parallel_tool_calls
        )

    def _handle_result(
        self, ctx: ChatProviderContext, result: ClaudeAgentSDKChatResult
    ) -> AIMessage:
        if result.usage:
            ctx.cost_recorder.add(self._get_cost_record(result))

        if result.stop_reason == "refusal":
            raise SafetyError()

        if result.stop_reason in ("max_tokens", "model_context_window_exceeded"):
            raise MaxTokenError()

        return result.ai_message

    def _get_cost_record(self, result: ClaudeAgentSDKChatResult) -> CostRecord:
        """A subscription is not billed per request, so the cost is 0."""
        usage = result.usage
        metadata: dict[str, Any] = {
            "model_name": self.settings.model_name,
            "input_tokens": usage.get("input_tokens", 0),
            "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
            "cached_input_tokens": usage.get("cache_read_input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }

        if result.total_cost_usd is not None:
            metadata["api_cost_microdollars"] = math.ceil(
                result.total_cost_usd * 1_000_000
            )

        return CostRecord(
            microdollars=0, kind="chat", source=self.name, metadata=metadata
        )


def _is_turn_limit(result_message: ResultMessage) -> bool:
    return result_message.subtype == "error_max_turns"


def _extract_overflow_token_count(message: str) -> int | None:
    match = re.search(r"prompt is too long:\s*(\d+)\s*tokens", message, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _to_ai_message_chunk(event: dict[str, Any]) -> AIMessageChunk | None:
    """The same raw Messages API events as the Anthropic provider streams."""
    event_type = event.get("type")

    if event_type == "content_block_start":
        block = event.get("content_block") or {}

        if block.get("type") == "tool_use":
            return AIMessageChunk(
                contents=[Content(text="")],
                tool_call_chunks=[
                    ToolCallChunk(
                        id=block.get("id"),
                        name=str(block.get("name") or "").removeprefix(
                            TOOL_NAME_PREFIX
                        ),
                        args="",
                        index=event.get("index"),
                    )
                ],
            )

    if event_type == "content_block_delta":
        delta = event.get("delta") or {}

        if delta.get("type") == "text_delta":
            return AIMessageChunk(contents=[Content(text=delta.get("text", ""))])

        if delta.get("type") == "input_json_delta":
            return AIMessageChunk(
                contents=[Content(text="")],
                tool_call_chunks=[
                    ToolCallChunk(
                        args=delta.get("partial_json", ""), index=event.get("index")
                    )
                ],
            )

    return None
