from typing import TypedDict

import pytest

from kiarina.agi.chat_content import MediaConverter
from kiarina.agi.chat_content._helpers.from_contents import (
    from_contents,
)
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.content import Content
from kiarina.agi.file_info import AudioFileInfo, ImageFileInfo, TextFileInfo
from kiarina.agi.run_context import RunContext


class ConversionArgs(TypedDict):
    capabilities: ChatCapabilities
    media_converter: MediaConverter
    run_context: RunContext


@pytest.fixture
def args(
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> ConversionArgs:
    return {
        "capabilities": capabilities,
        "media_converter": media_converter,
        "run_context": run_context,
    }


async def test_payload(args: ConversionArgs) -> None:
    result = await from_contents(
        "human",
        [Content(payload={"type": "text", "text": "Hello"})],
        **args,
    )

    assert len(result.parts) == 1
    assert len(result.purged_parts) == 0

    print(result)


async def test_text_and_files(
    text_file_info: TextFileInfo,
    image_file_info: ImageFileInfo,
    audio_file_info: AudioFileInfo,
    args: ConversionArgs,
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

    assert len(result.parts) == 5
    assert len(result.purged_parts) == 0

    print(result)


async def test_normalize(
    text_file_info: TextFileInfo, image_file_info: ImageFileInfo, args: ConversionArgs
) -> None:
    result = await from_contents(
        "human",
        [Content(text="Hello")],
        **args,
    )

    assert isinstance(result.normalized_parts, str)
    assert result.normalized_purged_parts == ""

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

    assert isinstance(result.normalized_parts, list)
    assert result.normalized_purged_parts == ""
