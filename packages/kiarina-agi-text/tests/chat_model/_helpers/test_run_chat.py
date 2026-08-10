from kiarina.agi.chat_model import run_chat
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, HumanMessage
from kiarina.agi.run_context import RunContext


async def test_run_chat(cost_recorder: CostRecorder, run_context: RunContext) -> None:
    message = None
    async for generated_message in run_chat(
        [HumanMessage.create("Hello")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        message = generated_message

    assert isinstance(message, AIMessage)
