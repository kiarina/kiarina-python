from typing import TypedDict

import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import ImageFileInfo
from kiarina.agi.langchain_chat_provider import LangChainMediaConverter, from_messages
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    SystemMessage,
    ToolCall,
    ToolMessage,
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


@pytest.fixture
def messages(image_file_info: ImageFileInfo) -> list[Message]:
    return [
        SystemMessage.create("You are a helpful assistant."),
        HumanMessage.create("Hello"),
        AIMessage.create("Hi! How can I help you?"),
        HumanMessage.create("Create a image of cute cat"),
        AIMessage.create(
            "Sure!",
            tool_calls=[
                ToolCall(
                    id="123",
                    name="create_image",
                    args={"prompt": "a cute cat"},
                )
            ],
        ),
        ToolMessage.create(
            f"image created:\n{image_file_info.to_metadata_only_xml()}",
            [image_file_info],
            tool_name="create_image",
            tool_call_args={"prompt": "a cute cat"},
            tool_call_id="123",
        ),
    ]


async def test_to_langchain_messages(
    messages: list[Message], args: ConversionArgs
) -> None:
    lc_messages = await from_messages(messages, **args)

    assert len(lc_messages) == 7

    for lc_message in lc_messages:
        print(f"--- {lc_message.__class__.__name__} ---")
        print(lc_message)
