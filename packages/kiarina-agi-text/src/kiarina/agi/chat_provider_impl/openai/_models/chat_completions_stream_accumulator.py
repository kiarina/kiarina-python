from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from kiarina.agi.content import Content
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCall, ToolCallChunk

from .._operations.from_completion_usage import from_completion_usage
from .._operations.from_finish_reason import from_finish_reason
from .._operations.parse_tool_call_args import parse_tool_call_args
from .._schemas.openai_chat_result import OpenAIChatResult
from .._schemas.openai_usage import OpenAIUsage

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionChunk


@dataclass
class _ToolCallBuffer:
    id: str = ""
    name: str = ""
    arguments: str = ""


@dataclass
class ChatCompletionsStreamAccumulator:
    """Builds the final result from Chat Completions stream chunks."""

    texts: list[str] = field(default_factory=list)
    tool_calls: dict[int, _ToolCallBuffer] = field(default_factory=dict)
    finish_reason: str | None = None
    usage: OpenAIUsage | None = None

    def add(self, chunk: "ChatCompletionChunk") -> AIMessageChunk | None:
        if chunk.usage:
            self.usage = from_completion_usage(chunk.usage)

        if not chunk.choices:
            return None

        choice = chunk.choices[0]

        if choice.finish_reason:
            self.finish_reason = choice.finish_reason

        text = choice.delta.content or choice.delta.refusal or ""
        tool_call_chunks: list[ToolCallChunk] = []

        for delta in choice.delta.tool_calls or []:
            buffer = self.tool_calls.setdefault(delta.index, _ToolCallBuffer())
            name = delta.function.name if delta.function else None
            arguments = delta.function.arguments if delta.function else None

            buffer.id += delta.id or ""
            buffer.name += name or ""
            buffer.arguments += arguments or ""

            tool_call_chunks.append(
                ToolCallChunk(id=delta.id, name=name, args=arguments, index=delta.index)
            )

        if not text and not tool_call_chunks:
            return None

        self.texts.append(text)

        return AIMessageChunk(
            contents=[Content(text=text)],
            tool_call_chunks=tool_call_chunks,
        )

    def to_result(self) -> OpenAIChatResult:
        return OpenAIChatResult(
            ai_message=AIMessage.create(
                text="".join(self.texts),
                tool_calls=[
                    ToolCall(
                        id=buffer.id,
                        name=buffer.name,
                        args=parse_tool_call_args(buffer.arguments),
                    )
                    for _, buffer in sorted(self.tool_calls.items())
                ],
            ),
            stop_reason=from_finish_reason(self.finish_reason),
            usage=self.usage,
        )
