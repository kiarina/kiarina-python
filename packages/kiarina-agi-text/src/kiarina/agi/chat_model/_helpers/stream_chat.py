from collections.abc import AsyncIterator

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo

from .._types.chat_options import ChatOptions
from .run_chat import run_chat


async def stream_chat(
    messages: list[Message],
    *,
    tool_infos: list[ToolInfo] | None = None,
    chat_options: ChatOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext | None = None,
) -> AsyncIterator[AIMessageChunk | AIMessage]:
    chat_options = chat_options or {}
    chat_options = {**chat_options, "streaming": True}

    async for ai_message in run_chat(
        messages,
        tool_infos=tool_infos,
        chat_options=chat_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        yield ai_message
