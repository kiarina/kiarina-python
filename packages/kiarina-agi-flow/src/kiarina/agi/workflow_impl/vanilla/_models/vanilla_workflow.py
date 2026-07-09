from kiarina.agi.state import StateContext
from kiarina.agi.state_impl.run import RunState
from kiarina.agi.state_machine import StateMachine
from kiarina.agi.workflow import workflow


@workflow
def VanillaWorkflow(ctx: StateContext) -> StateMachine:
    return StateMachine(
        ctx,
        states={
            "run": RunState(),
        },
    )
