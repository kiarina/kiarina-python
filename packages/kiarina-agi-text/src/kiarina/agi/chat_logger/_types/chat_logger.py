from contextlib import AbstractContextManager
from typing import Protocol, runtime_checkable

from kiarina.agi.message import AIMessage, AIMessageChunk
from kiarina.agi.run_context import RunContext

from .chat_logger_name import ChatLoggerName


@runtime_checkable
class ChatLogger(Protocol):
    name: ChatLoggerName

    def log_chat_invoke_start(
        self,
        run_context: RunContext,
    ) -> None: ...

    def log_chat_invoke_end(
        self,
        ai_message: AIMessage,
        run_context: RunContext,
    ) -> None: ...

    def log_chat_stream(
        self,
        run_context: RunContext,
    ) -> AbstractContextManager[None]: ...

    def log_chat_stream_chunk(
        self,
        ai_message_chunk: AIMessageChunk,
    ) -> None: ...
