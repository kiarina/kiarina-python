from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.state import StateContext
from kiarina.agi.state_machine import StateMachine
from kiarina.agi.workflow import workflow


@workflow
def Workflow(ctx: StateContext, custom_value: str = "hello") -> StateMachine:
    ctx.metadata["custom_value"] = custom_value
    return StateMachine(ctx)


async def test_workflow(
    history: History, cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    workflow_instance = Workflow(custom_value="world")

    state_machine = await workflow_instance.get_state_machine(
        history=history,
        chat_options={},
        prompt_options={},
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert state_machine.ctx.metadata["custom_value"] == "world"
