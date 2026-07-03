# mypy: ignore-errors

import pytest

from kiarina.agi.content import Content
from kiarina.agi.langchain_chat_provider._operations.from_contents import (
    from_contents,
)


@pytest.fixture
def args(capabilities, media_converter, run_context):
    return {
        "capabilities": capabilities,
        "media_converter": media_converter,
        "run_context": run_context,
    }


async def test_payload(args) -> None:
    result = await from_contents(
        "human",
        [Content(payload={"type": "text", "text": "Hello"})],
        **args,
    )

    assert len(result.lc_contents) == 1
    assert len(result.purged_lc_contents) == 0

    print(result)


async def test_text_and_files(
    text_file_info, image_file_info, audio_file_info, args
) -> None:
    result = await from_contents(
        "human",
        [
            Content(
                text="Hello",
                files=[text_file_info, image_file_info, audio_file_info],
            )
        ],
        **args,
    )

    assert len(result.lc_contents) == 5
    assert len(result.purged_lc_contents) == 0

    print(result)


async def test_normalize(text_file_info, image_file_info, args) -> None:
    result = await from_contents(
        "human",
        [Content(text="Hello")],
        **args,
    )

    assert isinstance(result.normalized_lc_contents, str)
    assert result.normalized_purged_lc_contents == ""

    result = await from_contents(
        "human",
        [
            Content(
                text="Hello",
                files=[text_file_info],
            )
        ],
        **args,
    )

    assert isinstance(result.normalized_lc_contents, list)
    assert result.normalized_purged_lc_contents == ""
