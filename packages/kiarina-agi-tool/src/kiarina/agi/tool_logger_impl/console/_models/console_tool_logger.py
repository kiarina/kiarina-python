import json
import sys

from kiarina.agi.console_utils import (
    divider,
    format_run_context,
    section_header,
    stderr_color,
)
from kiarina.agi.content import Content
from kiarina.agi.display_content import (
    DisplayContent,
    FileDisplayContent,
    TextDisplayContent,
)
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_utils import is_uri
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_logger import BaseToolLogger


class ConsoleToolLogger(BaseToolLogger):
    def log_tool_start(
        self,
        tool_call: ToolCall,
        run_context: RunContext,
    ) -> None:
        with stderr_color("cyan"):
            print(
                self._format_tool_start(tool_call, run_context),
                flush=True,
                file=sys.stderr,
            )

    def log_tool_end(
        self,
        tool_message: ToolMessage,
        run_context: RunContext,
    ) -> None:
        with stderr_color("green" if not tool_message.failed else "red"):
            print(
                self._format_tool_end(tool_message, run_context),
                flush=True,
                file=sys.stderr,
            )

    def _format_tool_start(
        self,
        tool_call: ToolCall,
        run_context: RunContext,
    ) -> str:
        lines = [
            "",
            "",
            section_header(f"TOOL CALL: {tool_call}"),
            format_run_context(run_context),
            divider(),
            "",
        ]

        if tool_call.args:
            lines.append(json.dumps(tool_call.args, indent=2, ensure_ascii=False))
            lines.append("")

        return "\n".join(lines)

    def _format_tool_end(
        self,
        tool_message: ToolMessage,
        run_context: RunContext,
    ) -> str:
        lines = [
            "",
            section_header(f"TOOL MESSAGE: {tool_message}"),
        ]

        if tool_message.return_direct or tool_message.artifact or tool_message.metadata:
            if tool_message.failed:
                lines.append("failed: True")

            if tool_message.return_direct:
                lines.append("return_direct: True")

            if tool_message.artifact:
                lines.append(f"artifacts: {', '.join(tool_message.artifact.keys())}")

            for key, value in tool_message.metadata.items():
                lines.append(f"{key}: {value}")

            lines.append(divider())

        if tool_message.contents:
            lines.append("")
            lines.append(self._format_contents(tool_message.contents))

        if tool_message.display_contents:
            lines.append("")
            lines.append(self._format_display_contents(tool_message.display_contents))

        return "\n".join(lines)

    # --------------------------------------------------
    # Content
    # --------------------------------------------------

    def _format_contents(self, contents: list[Content]) -> str:
        return "\n\n".join(self._format_content(content) for content in contents)

    def _format_content(self, content: Content) -> str:
        lines: list[str] = []

        for file_info in content.files:
            lines.append(self._format_file_info(file_info))

        if content.text:
            lines.append("")
            lines.append(content.text)

        return "\n".join(lines)

    def _format_file_info(self, file_info: FileInfo) -> str:
        parts = [
            f"[{file_info.type.upper()} FILE INFO]",
            file_info.uri,
        ]

        if file_info.name:
            parts.append(f"({file_info.name})")

        return " ".join(parts)

    # --------------------------------------------------
    # Display Content
    # --------------------------------------------------

    def _format_display_contents(self, display_contents: list[DisplayContent]) -> str:
        return "\n\n".join(
            self._format_display_content(display_content)
            for display_content in display_contents
        )

    def _format_display_content(self, display_content: DisplayContent) -> str:
        if display_content.type == "text":
            return self._format_text_display_content(display_content)
        elif display_content.type == "file":
            return self._format_file_display_content(display_content)
        else:
            raise AssertionError(
                f"Unknown display content type: {display_content.type}"
            )

    def _format_text_display_content(
        self,
        text_display_content: TextDisplayContent,
    ) -> str:
        lines = [
            f"[TEXT DISPLAY CONTENT] {text_display_content.mime_type}",
            section_header("START", fill_char="="),
            text_display_content.text,
            section_header("END", fill_char="="),
        ]

        return "\n".join(lines)

    def _format_file_display_content(
        self,
        file_display_content: FileDisplayContent,
    ) -> str:
        parts = [
            "[FILE DISPLAY CONTENT]",
            file_display_content.mime_type,
        ]

        if is_uri(file_display_content.uri_or_file_path):
            parts.append(file_display_content.uri_or_file_path)
        else:
            parts.append(f"file://{file_display_content.uri_or_file_path}")

        if file_display_content.display_name:
            parts.append(f"({file_display_content.display_name})")

        return " ".join(parts)
