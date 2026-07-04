from typing import Any

from kiarina.agi.chat_logger import BaseChatLogger
from kiarina.agi.message import AIMessage, AIMessageChunk


class MyChatLogger(BaseChatLogger):
    pass


def test_base_chat_logger(run_context: Any) -> None:
    chat_logger = MyChatLogger()
    chat_logger.log_chat_invoke_start(run_context)
    chat_logger.log_chat_invoke_end(AIMessage.create("test"), run_context)

    with chat_logger.log_chat_stream(run_context):
        chat_logger.log_chat_stream_chunk(AIMessageChunk.create("test"))
