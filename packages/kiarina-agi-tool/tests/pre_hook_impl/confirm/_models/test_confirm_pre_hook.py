from unittest.mock import patch

import pytest

from kiarina.agi.message import ToolCall
from kiarina.agi.pre_hook import PreHook, PreHookContext, PreHookError
from kiarina.agi.pre_hook_impl.confirm import ConfirmPreHook
from kiarina.agi.run_context import RunContext


@pytest.fixture
def hook() -> PreHook:
    hook = ConfirmPreHook()
    hook.name = "confirm"
    return hook


@pytest.fixture
def ctx(run_context: RunContext) -> PreHookContext:
    return PreHookContext.create(
        tool_call=ToolCall(name="run", id="call-1"),
        run_context=run_context,
    )


async def test_run_yes(hook: PreHook, ctx: PreHookContext) -> None:
    with patch("builtins.input", side_effect=["yes"]):
        events = [event async for event in hook.run(ctx)]

    assert events == []


async def test_run_y(hook: PreHook, ctx: PreHookContext) -> None:
    with patch("builtins.input", side_effect=["y"]):
        events = [event async for event in hook.run(ctx)]

    assert events == []


async def test_run_empty_as_yes(hook: PreHook, ctx: PreHookContext) -> None:
    with patch("builtins.input", side_effect=[""]):
        events = [event async for event in hook.run(ctx)]

    assert events == []


async def test_run_invalid_then_yes(
    hook: PreHook,
    ctx: PreHookContext,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input", side_effect=["maybe", "yes"]):
        [event async for event in hook.run(ctx)]

    captured = capsys.readouterr()
    assert "Please enter yes/y or no/n." in captured.out


async def test_run_no_with_reason(hook: PreHook, ctx: PreHookContext) -> None:
    with patch("builtins.input", side_effect=["no", "because"]):
        with pytest.raises(PreHookError, match="User rejected tool execution: because"):
            [event async for event in hook.run(ctx)]


async def test_run_n_without_reason(hook: PreHook, ctx: PreHookContext) -> None:
    with patch("builtins.input", side_effect=["n", ""]):
        with pytest.raises(PreHookError, match="User rejected tool execution"):
            [event async for event in hook.run(ctx)]
