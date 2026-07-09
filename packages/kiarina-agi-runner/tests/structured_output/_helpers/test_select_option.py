from collections.abc import Generator

import pytest

from kiarina.agi.chat_model import settings_manager
from kiarina.agi.run_context import RunContext
from kiarina.agi.structured_output import select_option


@pytest.fixture(autouse=True)
def setup() -> Generator[None, None, None]:
    settings_manager.cli_args = {"default": "mock"}
    yield
    settings_manager.cli_args = {}


async def test_select_option(run_context: RunContext) -> None:
    selected_option = await select_option(
        '{"tool_calls": [{"name": "banana", "args": {}}]}',
        options={
            "apple": "りんごが一番好きです。",
            "banana": "バナナが一番好きです。",
            "grape": "ぶどうが一番好きです。",
        },
        run_context=run_context,
    )

    assert selected_option == "banana"
