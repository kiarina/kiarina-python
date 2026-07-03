from collections.abc import AsyncIterator

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo

from .._models.chat_model import ChatModel
from .._services.chat_model_registry import chat_model_registry
from .._types.chat_options import ChatOptions


async def run_chat(
    messages: list[Message],
    *,
    tool_infos: list[ToolInfo] | None = None,
    chat_options: ChatOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> AsyncIterator[AIMessageChunk | AIMessage]:
    chat_options = chat_options or {}
    cost_recorder = cost_recorder or NullCostRecorder()

    chat_model = chat_options.get("chat_model")

    if not isinstance(chat_model, ChatModel):
        chat_model = chat_model_registry.resolve(chat_model)

    run_context = run_context.with_metadata(
        chat_model=str(chat_model),
    )

    async for ai_message in chat_model.run(
        messages,
        tool_infos=tool_infos,
        tool_choice=chat_options.get("tool_choice"),
        parallel_tool_calls=chat_options.get("parallel_tool_calls"),
        streaming=chat_options.get("streaming"),
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        yield ai_message
