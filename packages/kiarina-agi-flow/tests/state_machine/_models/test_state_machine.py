from collections.abc import AsyncIterator
from dataclasses import dataclass

from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.run_context import RunContext
from kiarina.agi.state import StateContext, StateName, state
from kiarina.agi.state_machine import StateMachine


@dataclass
class MyContext(StateContext):
    name: str = ""
    age: int = 0


@state
async def MyState1(
    ctx: MyContext,
    next_state: StateName | None = None,
) -> AsyncIterator[Event | StateName | None]:
    ctx.name = "kiarina"
    yield CustomEvent(payload={"message": "my_state_1"})
    yield next_state


@state
async def MyState2(
    ctx: MyContext,
    next_state: StateName | None = None,
) -> AsyncIterator[Event | StateName | None]:
    ctx.age = 14
    yield CustomEvent(payload={"message": "my_state_2"})
    yield next_state


async def test_state_machine(run_context: RunContext) -> None:
    ctx = MyContext.create(run_context=run_context)

    sm = StateMachine(
        ctx,
        states={
            "my_state_1": MyState1(next_state="my_state_2"),
            "my_state_2": MyState2(),
        },
    )

    events: list[Event] = []

    async for event in sm.run():
        events.append(event)

    assert len(events) == 2
    assert events[0].type == "custom"
    assert events[0].payload["message"] == "my_state_1"
    assert events[1].type == "custom"
    assert events[1].payload["message"] == "my_state_2"
    assert ctx.name == "kiarina"
    assert ctx.age == 14
