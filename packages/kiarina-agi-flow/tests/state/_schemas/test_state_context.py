from kiarina.agi.run_context import RunContext
from kiarina.agi.state import StateContext


def test_state_context(run_context: RunContext) -> None:
    ctx = StateContext.create(
        run_context=run_context,
        custom_arg="custom_value",
    )

    assert ctx.run_kwargs["custom_arg"] == "custom_value"
    print(ctx.to_dict())
