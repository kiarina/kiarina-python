from collections.abc import Iterator
from contextlib import contextmanager

from kiarina.agi.message import AIMessage, AIMessageChunk
from kiarina.agi.run_context import RunContext

from .._types.chat_logger import ChatLogger
from .._types.chat_logger_name import ChatLoggerName


class BaseChatLogger(ChatLogger):
    def __init__(self) -> None:
        self._name: ChatLoggerName | None = None

    @property
    def name(self) -> ChatLoggerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Chat logger name not set")

        return self._name

    @name.setter
    def name(self, value: ChatLoggerName) -> None:
        self._name = value

    def log_chat_invoke_start(self, run_context: RunContext) -> None:
        pass

    def log_chat_invoke_end(
        self,
        ai_message: AIMessage,
        run_context: RunContext,
    ) -> None:
        pass

    @contextmanager
    def log_chat_stream(self, run_context: RunContext) -> Iterator[None]:
        yield

    def log_chat_stream_chunk(self, ai_message_chunk: AIMessageChunk) -> None:
        pass
