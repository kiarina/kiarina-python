import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager

from kiarina.agi.chat_logger import BaseChatLogger
from kiarina.agi.console_utils import (
    divider,
    format_run_context,
    section_header,
    stderr_color,
)
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCall, ToolCallChunk
from kiarina.agi.run_context import RunContext

from .stream_printer import StreamPrinter


class ConsoleChatLogger(BaseChatLogger):
    def __init__(self) -> None:
        self.sp = StreamPrinter()
        self.require_padding = True

    # --------------------------------------------------
    # Public Methods (invoke)
    # --------------------------------------------------

    def log_chat_invoke_start(self, run_context: RunContext) -> None:
        with stderr_color("blue"):
            print(
                self._format_chat_start(run_context),
                flush=True,
                file=sys.stderr,
            )

    def log_chat_invoke_end(
        self,
        ai_message: AIMessage,
        run_context: RunContext,
    ) -> None:
        with stderr_color("yellow"):
            print(
                self._format_chat_end(ai_message),
                flush=True,
                file=sys.stderr,
            )

    # --------------------------------------------------
    # Public Methods (stream)
    # --------------------------------------------------

    @contextmanager
    def log_chat_stream(self, run_context: RunContext) -> Iterator[None]:
        with stderr_color("blue"):
            print(
                self._format_chat_start(run_context),
                flush=True,
                file=sys.stderr,
            )

        with stderr_color("yellow"):
            print(self._format_chat_end(), flush=True, file=sys.stderr)

            try:
                yield
            finally:
                print(flush=True, file=sys.stderr)

    def log_chat_stream_chunk(self, ai_message_chunk: AIMessageChunk) -> None:
        if ai_message_chunk.contents:
            if contents_text := ai_message_chunk.contents_to_text():
                self.sp(contents_text)
                self.require_padding = False

        if ai_message_chunk.tool_call_chunks:
            if self.require_padding:
                print(flush=True, file=sys.stderr)
                self.require_padding = False

            for tool_call_chunk in ai_message_chunk.tool_call_chunks:
                if tool_call_chunk.name:
                    print(
                        self._format_tool_call_chunk_name(tool_call_chunk),
                        flush=True,
                        file=sys.stderr,
                    )

                if tool_call_chunk.args:
                    try:
                        print(
                            self._format_tool_call_chunk_args(tool_call_chunk),
                            flush=True,
                            file=sys.stderr,
                        )

                    except Exception:
                        self.sp(tool_call_chunk.args)

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _format_chat_start(self, run_context: RunContext) -> str:
        lines = [
            "",
            "",
            section_header("AI CALL"),
            format_run_context(run_context),
            divider(),
        ]

        return "\n".join(lines)

    def _format_chat_end(self, ai_message: AIMessage | None = None) -> str:
        lines = [
            "",
            "",
            section_header("AI MESSAGE"),
            "",
        ]

        if ai_message:
            lines.append(self._format_ai_message(ai_message))

        return "\n".join(lines)

    def _format_ai_message(self, ai_message: AIMessage) -> str:
        lines: list[str] = []

        if contents_text := ai_message.contents_to_text():
            lines.append(contents_text)

        for tool_call in ai_message.tool_calls:
            lines.append(self._format_tool_call(tool_call))

        return "\n".join(lines)

    def _format_tool_call(self, tool_call: ToolCall) -> str:
        lines = [
            "",
            "",
            f"[TOOL CALL] {tool_call}",
        ]

        if tool_call.args:
            lines.append(json.dumps(tool_call.args, indent=2, ensure_ascii=False))

        return "\n".join(lines)

    def _format_tool_call_chunk_name(self, tool_call_chunk: ToolCallChunk) -> str:
        lines = [
            "",
            "",
            f"[TOOL CALL] {tool_call_chunk.name}",
        ]

        return "\n".join(lines)

    def _format_tool_call_chunk_args(self, tool_call_chunk: ToolCallChunk) -> str:
        assert tool_call_chunk.args is not None
        return json.dumps(
            json.loads(tool_call_chunk.args), indent=2, ensure_ascii=False
        )
