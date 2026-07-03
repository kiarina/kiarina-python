# mypy: ignore-errors

from kiarina.agi.chat_logger_impl.console import ConsoleChatLogger
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCall, ToolCallChunk


def test_invoke(run_context) -> None:
    chat_logger = ConsoleChatLogger()
    chat_logger.log_chat_invoke_start(run_context)
    chat_logger.log_chat_invoke_end(
        AIMessage.create(
            "test",
            tool_calls=[
                ToolCall(
                    name="test_tool",
                    args={"arg1": "value1"},
                ),
            ],
        ),
        run_context,
    )


def test_stream(run_context) -> None:
    chat_logger = ConsoleChatLogger()

    with chat_logger.log_chat_stream(run_context):
        s = "hello"

        for i in range(len(s)):
            chat_logger.log_chat_stream_chunk(AIMessageChunk.create(s[i]))

        chat_logger.log_chat_stream_chunk(
            AIMessageChunk(
                tool_call_chunks=[
                    ToolCallChunk(
                        name="test_tool",
                        args='{"arg1": "value1"}',
                    )
                ]
            )
        )
