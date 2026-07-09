from collections.abc import AsyncIterator, Sequence
from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext

from .._schemas.pre_hook_context import PreHookContext
from .._services.pre_hook_registry import pre_hook_registry
from .._types.pre_hook import PreHook
from .._types.pre_hook_name import PreHookName


async def run_pre_hooks(
    tool_call: ToolCall,
    hooks: Sequence[PreHook | PreHookName],
    *,
    history: History | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    ctx = PreHookContext.create(
        tool_call=tool_call,
        history=history,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    )

    for hook in hooks:
        if not isinstance(hook, PreHook):
            hook = pre_hook_registry.resolve(hook)

        async for event in hook.run(ctx):
            yield event
