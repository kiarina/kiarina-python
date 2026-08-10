from collections.abc import AsyncIterator

from kiarina.agi.event import Event
from kiarina.agi.prompt import run_prompt
from kiarina.agi.state import StateContext, StateName, state


@state
async def RunState(
    ctx: StateContext,
    next_state: StateName | None = None,
) -> AsyncIterator[Event | StateName | None]:
    async for event in run_prompt(
        ctx.history,
        chat_options=ctx.chat_options,
        prompt_options=ctx.prompt_options,
        cost_recorder=ctx.cost_recorder,
        run_context=ctx.run_context,
        **ctx.run_kwargs,
    ):
        yield event

    yield next_state
