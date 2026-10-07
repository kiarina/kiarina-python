import asyncio
import os
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter, to_transcript
from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
    TokenOverflowError,
)
from kiarina.agi.content import Content
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCallChunk
from kiarina.utils.mime import MIMEBlob

from .._operations.create_config_overrides import create_config_overrides
from .._operations.create_model_catalog import create_model_catalog
from .._operations.from_raw_response_items import from_raw_response_items
from .._operations.to_dynamic_tools import to_dynamic_tools
from .._schemas.codex_app_server_chat_result import CodexAppServerChatResult
from .._settings import CodexAppServerChatProviderSettings
from .codex_app_server_session import CodexAppServerSession

try:
    import codex_cli_bin  # type: ignore[import-untyped]
except ImportError as exc:
    raise ImportError(
        "openai-codex-cli-bin is required to use CodexAppServerChatProvider. "
        "Install it with: pip install 'kiarina-agi-text[chat-provider-codex-app-server]'"
    ) from exc

_CLIENT_INFO = {"name": "kiarina-agi-text", "title": "kiarina-agi-text", "version": "1"}


class CodexAppServerChatProvider(BaseChatProvider, MediaConverter):
    """
    Codex App Server Chat Provider Implementation

    Runs `codex app-server` with its own login, one new process and ephemeral
    thread per request. The conversation is sent as one `<messages>` XML prompt,
    Codex's own tools and instructions are turned off, and the process is closed
    when the first model response completes. Tool call requests are never
    answered, so the caller runs the tools.

    Codex sends app tools with `parallel_tool_calls: false`, so a turn has at most
    one tool call.
    """

    def __init__(self, settings: CodexAppServerChatProviderSettings) -> None:
        super().__init__()

        self.settings: CodexAppServerChatProviderSettings = settings

    def __str__(self) -> str:
        props: list[str] = [self.settings.model_name]

        if self.settings.reasoning_effort:
            props.append(self.settings.reasoning_effort)

        return f"{self.__class__.__name__}({', '.join(props)})"

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def codex_home(self) -> Path:
        home = self.settings.codex_home or os.environ.get("CODEX_HOME")
        return Path(home).expanduser() if home else Path.home() / ".codex"

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
            "url": f"data:{mime_blob.mime_type};base64,{mime_blob.raw_base64_str}",
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
        user_input: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": transcript.to_user_prompt(
                    tool_choice=ctx.tool_choice if tool_infos else None
                ),
            },
            *transcript.media_parts,
        ]

        chat_logger = chat_logger_registry.resolve()

        with tempfile.TemporaryDirectory(prefix="kiarina-codex-app-server-") as tmp:
            session = self.create_session(Path(tmp))
            thread_params: dict[str, Any] = {
                "cwd": tmp,
                "ephemeral": True,
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "baseInstructions": system_prompt,
                "model": self.settings.model_name,
                "dynamicTools": to_dynamic_tools(tool_infos),
                "experimentalRawEvents": True,
            }

            if ctx.streaming:
                with chat_logger.log_chat_stream(ctx.run_context):
                    async for item in self._turn(session, thread_params, user_input):
                        if isinstance(item, AIMessageChunk):
                            chat_logger.log_chat_stream_chunk(item)
                            yield item
                        else:
                            yield self._handle_result(ctx, item)
            else:
                chat_logger.log_chat_invoke_start(ctx.run_context)

                async for item in self._turn(session, thread_params, user_input):
                    if isinstance(item, CodexAppServerChatResult):
                        ai_message = self._handle_result(ctx, item)
                        chat_logger.log_chat_invoke_end(ai_message, ctx.run_context)
                        yield ai_message

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def create_session(self, tmp: Path) -> CodexAppServerSession:
        codex_home = self.codex_home
        catalog_path = create_model_catalog(
            codex_home, self.settings.model_name, tmp / "models.json"
        )

        args = [self.settings.codex_bin or str(codex_cli_bin.bundled_codex_path())]

        for override in [
            *create_config_overrides(codex_home, catalog_path),
            *self.settings.config_overrides,
        ]:
            args += ["--config", override]

        args += ["app-server", "--listen", "stdio://"]

        env = {**os.environ, **self.settings.env}

        if self.settings.codex_bin is None and (
            path_dir := codex_cli_bin.bundled_path_dir()
        ):
            env["PATH"] = os.pathsep.join([str(path_dir), env.get("PATH", "")])

        return CodexAppServerSession(args, env=env, cwd=str(tmp))

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    async def _turn(
        self,
        session: CodexAppServerSession,
        thread_params: dict[str, Any],
        user_input: list[dict[str, Any]],
    ) -> AsyncIterator[AIMessageChunk | CodexAppServerChatResult]:
        items: list[dict[str, Any]] = []

        try:
            async with asyncio.timeout(self.settings.timeout):
                await session.start()
                await session.request(
                    "initialize",
                    {
                        "clientInfo": _CLIENT_INFO,
                        "capabilities": {"experimentalApi": True},
                    },
                )
                await session.notify("initialized", None)

                thread = await session.request("thread/start", thread_params)
                turn_params: dict[str, Any] = {
                    "threadId": thread["thread"]["id"],
                    "input": user_input,
                }

                if self.settings.reasoning_effort:
                    turn_params["effort"] = self.settings.reasoning_effort

                await session.request("turn/start", turn_params)

                while True:
                    event = await session.next_event()
                    method = event["method"]
                    params = event.get("params") or {}

                    if method == "item/agentMessage/delta":
                        if delta := params.get("delta"):
                            yield AIMessageChunk(contents=[Content(text=delta)])

                    elif method == "rawResponseItem/completed":
                        item = params.get("item") or {}
                        items.append(item)

                        if item.get("type") == "function_call":
                            index = sum(i.get("type") == "function_call" for i in items)
                            yield _to_tool_call_chunk(item, index=index - 1)

                    elif method == "rawResponse/completed":
                        # NOTE: The model turn is complete. A tool call request,
                        # if any, is left unanswered.
                        yield from_raw_response_items(items, params.get("usage"))
                        return

                    elif method == "error" and not params.get("willRetry"):
                        self._raise_turn_error(params.get("error") or {})

                    elif method == "turn/completed":
                        self._raise_turn_error(
                            (params.get("turn") or {}).get("error")
                            or {"message": "The turn ended without a response."}
                        )

                    elif method == "_closed":
                        raise RuntimeError(
                            f"codex app-server exited. stderr: {session.stderr_tail[-2000:]}"
                        )
        finally:
            await session.close()

    def _raise_turn_error(self, error: dict[str, Any]) -> None:
        if error.get("codexErrorInfo") == "contextWindowExceeded":
            # NOTE: The error has no token count.
            raise TokenOverflowError(self.settings.context_window)

        raise RuntimeError(f"Codex failed: {error.get('message') or error}")

    def _handle_result(
        self, ctx: ChatProviderContext, result: CodexAppServerChatResult
    ) -> AIMessage:
        if result.usage:
            ctx.cost_recorder.add(self._get_cost_record(result.usage))

        return result.ai_message

    def _get_cost_record(self, usage: dict[str, Any]) -> CostRecord:
        """A subscription is not billed per request, so the cost is 0."""
        cached_input_tokens = usage.get("cachedInputTokens") or 0

        return CostRecord(
            microdollars=0,
            kind="chat",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": (usage.get("inputTokens") or 0) - cached_input_tokens,
                "cached_input_tokens": cached_input_tokens,
                "output_tokens": usage.get("outputTokens") or 0,
                "reasoning_output_tokens": usage.get("reasoningOutputTokens") or 0,
            },
        )


def _to_tool_call_chunk(item: dict[str, Any], *, index: int) -> AIMessageChunk:
    """A function call arrives whole."""
    arguments = item.get("arguments")

    return AIMessageChunk(
        contents=[Content(text="")],
        tool_call_chunks=[
            ToolCallChunk(
                id=item.get("call_id"),
                name=item.get("name"),
                args=arguments if isinstance(arguments, str) else "",
                index=index,
            )
        ],
    )
