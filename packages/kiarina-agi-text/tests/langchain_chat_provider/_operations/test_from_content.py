# mypy: ignore-errors

import pytest

from kiarina.agi.content import Content
from kiarina.agi.langchain_chat_provider._operations.from_content import (
    from_content,
)


@pytest.fixture
def args(capabilities, media_converter, run_context):
    return {
        "capabilities": capabilities,
        "media_converter": media_converter,
        "run_context": run_context,
    }


async def test_human(text_file_info, image_file_info, args) -> None:
    result = await from_content(
        message_type="human",
        content=Content(
            text="Hello",
            files=[text_file_info, text_file_info, image_file_info],
            cache_control={"type": "ephemeral"},
        ),
        **args,
    )

    assert len(result.lc_contents) == 4
    assert len(result.purged_lc_contents) == 0

    print(result)


async def test_tool(text_file_info, image_file_info, args) -> None:
    result = await from_content(
        message_type="tool",
        content=Content(
            text="Hello",
            files=[text_file_info, text_file_info, image_file_info],
        ),
        **args,
    )

    assert len(result.lc_contents) == 2
    assert len(result.purged_lc_contents) == 2

    print(result)
