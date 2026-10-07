import asyncio
import logging
import os
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter
from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
    ChatProviderState,
    TokenOverflowError,
    compute_history_hash,
    find_chat_provider_state,
)
from kiarina.agi.content import Content
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk, Message, ToolCallChunk
from kiarina.agi.tool_info import ToolChoice, ToolInfo
from kiarina.utils.mime import MIMEBlob

from .._instances.live_thread_pool import live_thread_pool
from .._operations.create_config_overrides import create_config_overrides
from .._operations.create_model_catalog import create_model_catalog
from .._operations.from_raw_response_items import from_raw_response_items
from .._operations.to_dynamic_tools import to_dynamic_tools
from .._operations.to_thread_items import to_thread_items
from .._schemas.codex_chat_result import CodexChatResult
from .._schemas.codex_request import CodexRequest
from .._settings import CodexChatProviderSettings
from .codex_app_server_session import CodexAppServerSession
from .live_thread import LiveThread

try:
    import codex_cli_bin  # type: ignore[import-untyped]
except ImportError as exc:
    raise ImportError(
        "openai-codex-cli-bin is required to use CodexChatProvider. "
        "Install it with: pip install 'kiarina-agi-text[chat-provider-codex]'"
    ) from exc

logger = logging.getLogger(__name__)

_CLIENT_INFO = {"name": "kiarina-agi-text", "title": "kiarina-agi-text", "version": "1"}

_DEFAULT_INSTRUCTIONS = "You are a helpful assistant."
"""Without base instructions, Codex would send its own."""


class CodexChatProvider(BaseChatProvider, MediaConverter):
    """
    Codex Chat Provider Implementation

    Runs `codex app-server` with its own login, with a process and ephemeral
    thread per conversation. The conversation is injected into the thread as raw
    Responses API items, as the API would get it, and the turn starts with no
    input. Codex's own tools and instructions are turned off. A request ends when
    the model response completes, with its tool call requests held unanswered,
    so the caller runs the tools.

    Codex sends app tools with `parallel_tool_calls: false`, so a turn has at most
    one tool call.

    With `thread_reuse`, the process and thread are kept after a response, and a
    `ChatProviderState` on the returned `AIMessage` records the thread and the
    history hash. When the next request extends that history, a paused turn gets
    the tool results as answers to its held requests, or a completed turn gets
    the new messages and a new turn. Codex reads the prompt cache only within a
    thread. Any mismatch or failure starts a new thread instead.
    """

    def __init__(self, settings: CodexChatProviderSettings) -> None:
        super().__init__()

        self.settings: CodexChatProviderSettings = settings

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
            "type": "input_image",
            "image_url": f"data:{mime_blob.mime_type};base64,{mime_blob.raw_base64_str}",
        }

    # --------------------------------------------------
    # Methods (BaseChatProvider)
    # --------------------------------------------------

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        tool_infos = ctx.tool_infos or []
        request = await self._convert(
            ctx, ctx.messages, ctx.tool_choice if tool_infos else None
        )
        thread_header = self._thread_header(request, tool_infos)
        chat_logger = chat_logger_registry.resolve()
        response: tuple[CodexChatResult, LiveThread] | None = None

        if ctx.streaming:
            with chat_logger.log_chat_stream(ctx.run_context):
                async for item in self._respond(ctx, request, thread_header):
                    if isinstance(item, AIMessageChunk):
                        chat_logger.log_chat_stream_chunk(item)
                        yield item
                    else:
                        response = item
        else:
            chat_logger.log_chat_invoke_start(ctx.run_context)

            async for item in self._respond(ctx, request, thread_header):
                if not isinstance(item, AIMessageChunk):
                    response = item

        if response is None:  # pragma: no cover
            raise AssertionError("Empty response")

        result, live = response

        try:
            ai_message = self._handle_result(ctx, result)
            await self._keep_thread(ctx, request, thread_header, live, ai_message)
        except BaseException:
            await live.close()
            raise

        if not ctx.streaming:
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

    async def _convert(
        self,
        ctx: ChatProviderContext,
        messages: list[Message],
        tool_choice: ToolChoice | None,
    ) -> CodexRequest:
        return await to_thread_items(
            messages,
            tool_choice=tool_choice,
            capabilities=ctx.capabilities,
            media_converter=self,
            run_context=ctx.run_context,
        )

    def _thread_header(
        self, request: CodexRequest, tool_infos: list[ToolInfo]
    ) -> dict[str, Any]:
        """What a thread is started with. A thread is continued only if it matches."""
        return {
            "model": self.settings.model_name,
            "effort": self.settings.reasoning_effort,
            "instructions": request.instructions or _DEFAULT_INSTRUCTIONS,
            "tools": to_dynamic_tools(tool_infos),
        }

    async def _respond(
        self,
        ctx: ChatProviderContext,
        request: CodexRequest,
        thread_header: dict[str, Any],
    ) -> AsyncIterator[AIMessageChunk | tuple[CodexChatResult, LiveThread]]:
        async with asyncio.timeout(self.settings.timeout):
            if live := self._take_live_thread(ctx.messages, request, thread_header):
                yielded = False

                try:
                    async for item in self._resume(live):
                        yielded = yielded or isinstance(item, AIMessageChunk)
                        yield item

                    return
                except Exception:
                    await live.close()

                    if yielded:
                        raise

                    logger.info(
                        "Could not continue Codex thread %s; starting a new one.",
                        live.thread_id,
                        exc_info=True,
                    )

            live = self._new_live_thread()

            try:
                await self._start_thread(live, request, thread_header)

                async for item in self._read_response(live):
                    yield item
            except BaseException:
                await live.close()
                raise

    def _take_live_thread(
        self,
        messages: list[Message],
        request: CodexRequest,
        thread_header: dict[str, Any],
    ) -> LiveThread | None:
        """The kept thread the request continues, ready to resume, if any."""
        if not self.settings.thread_reuse:
            return None

        found = find_chat_provider_state(messages, self.name)

        if found is None:
            return None

        index, state = found
        thread_id = state.data.get("thread_id")
        live = live_thread_pool.take(thread_id) if isinstance(thread_id, str) else None

        if live is None:
            return None

        end = request.item_ends[index]
        tail = request.items[end:]
        history_hash = _hash_history(thread_header, request.items[:end])

        if not (state.history_hash == live.history_hash == history_hash) or not tail:
            live.kill()
            return None

        if live.pending_call_ids:
            # NOTE: A paused turn takes only the results of its tool calls.
            call_ids = [item.get("call_id") for item in tail]

            if (
                request.instruction_item is not None
                or any(item.get("type") != "function_call_output" for item in tail)
                or sorted(map(str, call_ids)) != sorted(live.pending_call_ids)
            ):
                live.kill()
                return None

            live.outputs = {
                str(item["call_id"]): _to_tool_reply(item.get("output"))
                for item in tail
            }
        else:
            live.next_items = (
                [*tail, request.instruction_item] if request.instruction_item else tail
            )

        return live

    def _new_live_thread(self) -> LiveThread:
        directory = tempfile.TemporaryDirectory(prefix="kiarina-codex-app-server-")

        try:
            session = self.create_session(Path(directory.name))
        except BaseException:
            directory.cleanup()
            raise

        return LiveThread(session=session, directory=directory)

    async def _start_thread(
        self,
        live: LiveThread,
        request: CodexRequest,
        thread_header: dict[str, Any],
    ) -> None:
        session = live.session
        await session.start()
        await session.request(
            "initialize",
            {"clientInfo": _CLIENT_INFO, "capabilities": {"experimentalApi": True}},
        )
        await session.notify("initialized", None)

        thread = await session.request(
            "thread/start",
            {
                "cwd": live.directory.name,
                "ephemeral": True,
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "baseInstructions": thread_header["instructions"],
                "model": thread_header["model"],
                "dynamicTools": thread_header["tools"],
                "experimentalRawEvents": True,
            },
        )
        live.thread_id = thread["thread"]["id"]

        if request.injected_items:
            await session.request(
                "thread/inject_items",
                {"threadId": live.thread_id, "items": request.injected_items},
            )

        await self._start_turn(live)

    async def _start_turn(self, live: LiveThread) -> None:
        params: dict[str, Any] = {"threadId": live.thread_id, "input": []}

        if self.settings.reasoning_effort:
            params["effort"] = self.settings.reasoning_effort

        turn = await live.session.request("turn/start", params)
        live.turn_id = turn["turn"]["id"]
        live.turn_completed = False
        live.held_requests = {}
        live.pending_call_ids = []

    async def _resume(
        self, live: LiveThread
    ) -> AsyncIterator[AIMessageChunk | tuple[CodexChatResult, LiveThread]]:
        if live.pending_call_ids:
            # NOTE: Answer the held requests. Codex asks for one tool call at a
            # time, so the rest are answered as they arrive.
            for call_id, request_id in list(live.held_requests.items()):
                if call_id in live.outputs:
                    await live.session.respond(request_id, live.outputs.pop(call_id))
                    del live.held_requests[call_id]

            live.pending_call_ids = []
        else:
            await self._wait_turn_completed(live)
            await live.session.request(
                "thread/inject_items",
                {"threadId": live.thread_id, "items": live.next_items},
            )
            live.next_items = []
            await self._start_turn(live)

        async for item in self._read_response(live):
            yield item

    async def _wait_turn_completed(self, live: LiveThread) -> None:
        while not live.turn_completed:
            event = await live.session.next_event()
            method = event["method"]
            params = event.get("params") or {}

            if method == "turn/completed" and _event_turn_id(params) == live.turn_id:
                live.turn_completed = True
            elif method == "_closed":
                raise RuntimeError("codex app-server exited.")

    async def _read_response(
        self, live: LiveThread
    ) -> AsyncIterator[AIMessageChunk | tuple[CodexChatResult, LiveThread]]:
        """Read the turn's next model response, answering known tool calls."""
        session = live.session
        items: list[dict[str, Any]] = []

        while True:
            event = await session.next_event()
            method = event["method"]
            params = event.get("params") or {}

            if "id" in event:
                # NOTE: A request from the server. A tool call is answered with
                # a known result, or held, which keeps Codex from going on.
                if method == "item/tool/call":
                    call_id = str(params.get("callId"))

                    if call_id in live.outputs:
                        await session.respond(event["id"], live.outputs.pop(call_id))
                    else:
                        live.held_requests[call_id] = event["id"]

                continue

            if _event_turn_id(params) not in (None, live.turn_id):
                continue

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
                # NOTE: The model response is complete. Its tool calls wait for
                # results from the caller.
                result = from_raw_response_items(items, params.get("usage"))
                live.pending_call_ids = [tc.id for tc in result.ai_message.tool_calls]
                yield result, live
                return

            elif method == "error" and not params.get("willRetry"):
                self._raise_turn_error(params.get("error") or {})

            elif method == "turn/completed":
                live.turn_completed = True
                self._raise_turn_error(
                    (params.get("turn") or {}).get("error")
                    or {"message": "The turn ended without a response."}
                )

            elif method == "_closed":
                raise RuntimeError(
                    f"codex app-server exited. stderr: {session.stderr_tail[-2000:]}"
                )

    async def _keep_thread(
        self,
        ctx: ChatProviderContext,
        request: CodexRequest,
        thread_header: dict[str, Any],
        live: LiveThread,
        ai_message: AIMessage,
    ) -> None:
        """Keep the thread for the next request, or close it."""
        if not self.settings.thread_reuse or request.instruction_item is not None:
            # NOTE: A forced tool choice stays in the thread as a developer
            # message, which a later turn should not see.
            await live.close()
            return

        ai_items = (await self._convert(ctx, [ai_message], None)).items
        live.history_hash = _hash_history(thread_header, [*request.items, *ai_items])
        ChatProviderState(
            name=self.name,
            history_hash=live.history_hash,
            data={"thread_id": live.thread_id},
        ).write_to(ai_message)
        live_thread_pool.put(
            live,
            idle_timeout=self.settings.thread_idle_timeout,
            max_count=self.settings.max_live_threads,
        )

    def _raise_turn_error(self, error: dict[str, Any]) -> None:
        if error.get("codexErrorInfo") == "contextWindowExceeded":
            # NOTE: The error has no token count.
            raise TokenOverflowError(self.settings.context_window)

        raise RuntimeError(f"Codex failed: {error.get('message') or error}")

    def _handle_result(
        self, ctx: ChatProviderContext, result: CodexChatResult
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
                "cache_write_tokens": usage.get("cacheWriteInputTokens") or 0,
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


def _hash_history(thread_header: dict[str, Any], items: list[dict[str, Any]]) -> str:
    return compute_history_hash({"thread": thread_header, "items": items})


def _event_turn_id(params: dict[str, Any]) -> str | None:
    turn_id = params.get("turnId") or (params.get("turn") or {}).get("id")
    return str(turn_id) if turn_id else None


def _to_tool_reply(output: Any) -> dict[str, Any]:
    """A `function_call_output` as the reply to a dynamic tool call request."""
    if isinstance(output, str):
        return {
            "contentItems": [{"type": "inputText", "text": output}],
            "success": True,
        }

    content_items: list[dict[str, Any]] = []

    for part in output or []:
        if part.get("type") == "input_text":
            content_items.append({"type": "inputText", "text": part.get("text", "")})
        elif part.get("type") == "input_image":
            content_items.append(
                {"type": "inputImage", "imageUrl": part.get("image_url", "")}
            )

    return {"contentItems": content_items, "success": True}
