from typing import Any

from kiarina.agi.chat_model import run_chat
from kiarina.agi.message import AIMessage, HumanMessage


async def test_run_chat(cost_recorder: Any, run_context: Any) -> None:
    message = None
    async for generated_message in run_chat(
        [HumanMessage.create("Hello")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        message = generated_message

    assert isinstance(message, AIMessage)
