from collections.abc import AsyncIterator

from kiarina.agi.event import Event
from kiarina.agi.state import State, StateContext, StateName


class StateMachine:
    def __init__(
        self,
        ctx: StateContext,
        *,
        states: dict[StateName, State] | None = None,
        start_state_name: StateName | None = None,
    ) -> None:
        self.ctx: StateContext = ctx
        self.states: dict[StateName, State] = states or {}
        self.start_state_name: StateName | None = start_state_name

    def add_state(self, state_name: StateName, state: State) -> None:
        self.states[state_name] = state

    def get_state(self, state_name: StateName) -> State:
        if state_name not in self.states:
            raise ValueError(f"State '{state_name}' not found in the state machine.")

        return self.states[state_name]

    async def run(self) -> AsyncIterator[Event]:
        if not self.states:
            raise ValueError("State machine has no states defined.")

        current: StateName | None = self.start_state_name

        if not current:
            current = next(iter(self.states))

        while current is not None:
            state = self.get_state(current)
            next_state: StateName | None = None

            self.ctx.run_context = self.ctx.run_context.with_metadata(
                state=current,
            )

            async for item in state.run(self.ctx):
                if isinstance(item, Event):
                    yield item
                else:
                    next_state = item

            current = next_state
