from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo

from .._types.chat_options import ChatOptions
from .run_chat import run_chat


async def invoke_chat(
    messages: list[Message],
    *,
    tool_infos: list[ToolInfo] | None = None,
    chat_options: ChatOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> AIMessage:
    chat_options = chat_options or {}
    chat_options = {**chat_options, "streaming": False}

    ai_message: AIMessage | None = None

    async for generated_message in run_chat(
        messages,
        tool_infos=tool_infos,
        chat_options=chat_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        ai_message = generated_message

    if ai_message is None:  # pragma: no cover
        raise RuntimeError("AI message was not generated")

    return ai_message
