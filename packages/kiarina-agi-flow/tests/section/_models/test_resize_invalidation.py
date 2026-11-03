import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from typing import cast

import pytest

from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.section import BaseSection
from kiarina.agi.token_utils import TokenCount


class ChangingSection(BaseSection):
    def __init__(self, action: str) -> None:
        super().__init__()
        self.text = "old " * 100
        self.action = action
        self.entered = asyncio.Event()

    def get_system_texts(self) -> list[str]:
        return [self.text]

    async def _resize(self, reduce: TokenCount) -> AsyncIterator[Event]:
        self.text = "new"
        if self.action == "raise":
            raise ValueError("failed after changing the view")
        if self.action == "cancel":
            self.entered.set()
            await asyncio.Event().wait()
        yield CustomEvent.create(type="changed")


@pytest.mark.parametrize("action", ["complete", "raise", "close", "cancel"])
async def test_resize_invalidates_estimates_on_all_exit_paths(action: str) -> None:
    section = ChangingSection(action)
    before = section.get_estimates()
    assert section.get_estimates() is before
    resize = cast(AsyncGenerator[Event, None], section.resize(100))
    if action == "raise":
        with pytest.raises(ValueError):
            await anext(resize)
    elif action == "close":
        await anext(resize)
        await resize.aclose()
    elif action == "cancel":

        async def advance() -> Event:
            return await anext(resize)

        task = asyncio.create_task(advance())
        await section.entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        assert len([event async for event in resize]) == 1
    after = section.get_estimates()
    assert after is not before
    assert after.token_count < before.token_count
