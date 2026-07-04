from typing import TypedDict

import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.content import Content
from kiarina.agi.file_info import ImageFileInfo, TextFileInfo
from kiarina.agi.langchain_chat_provider import LangChainMediaConverter
from kiarina.agi.langchain_chat_provider._operations.from_content import (
    from_content,
)
from kiarina.agi.run_context import RunContext


class ConversionArgs(TypedDict):
    capabilities: ChatCapabilities
    media_converter: LangChainMediaConverter
    run_context: RunContext


@pytest.fixture
def args(
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> ConversionArgs:
    return {
        "capabilities": capabilities,
        "media_converter": media_converter,
        "run_context": run_context,
    }


async def test_human(
    text_file_info: TextFileInfo, image_file_info: ImageFileInfo, args: ConversionArgs
) -> None:
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


async def test_tool(
    text_file_info: TextFileInfo, image_file_info: ImageFileInfo, args: ConversionArgs
) -> None:
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
