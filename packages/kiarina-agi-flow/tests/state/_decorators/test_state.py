from collections.abc import AsyncIterator

from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.run_context import RunContext
from kiarina.agi.state import StateContext, StateName, state


async def test_state(run_context: RunContext) -> None:
    @state
    async def MyState(
        ctx: StateContext,
        message: str,
        next_state: StateName,
    ) -> AsyncIterator[Event | StateName | None]:
        yield CustomEvent(payload={"message": message})
        yield next_state

    my_state = MyState(
        message="Hello",
        next_state="fuga",
    )

    event: Event | None = None
    next_state: StateName | None = None

    async for item in my_state.run(
        StateContext.create(run_context=run_context),
    ):
        if isinstance(item, Event):
            event = item
        elif isinstance(item, str):
            next_state = item

    assert event is not None
    assert event.type == "custom"
    assert event.payload["message"] == "Hello"
    assert next_state == "fuga"
