# mypy: ignore-errors

from kiarina.agi.chat_logger_impl.null import NullChatLogger
from kiarina.agi.message import AIMessage, AIMessageChunk


def test_null_chat_logger(run_context) -> None:
    chat_logger = NullChatLogger()
    chat_logger.log_chat_invoke_start(run_context)
    chat_logger.log_chat_invoke_end(AIMessage.create("test"), run_context)

    with chat_logger.log_chat_stream(run_context):
        chat_logger.log_chat_stream_chunk(AIMessageChunk.create("test"))
