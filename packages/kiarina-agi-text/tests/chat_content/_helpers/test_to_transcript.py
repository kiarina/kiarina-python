from kiarina.agi.chat_content import MediaConverter, to_transcript
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import ImageFileInfo
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext


async def test_to_transcript(
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> None:
    tool_message = ToolMessage.create(
        "rain", tool_name="get_weather", tool_call_id="call_1"
    )
    tool_message.failed = True

    transcript = await to_transcript(
        [
            SystemMessage.create("Be brief."),
            HumanMessage.create("Weather?"),
            AIMessage.create(
                "Checking.",
                tool_calls=[
                    ToolCall(id="call_1", name="get_weather", args={"city": "名古屋"})
                ],
            ),
            tool_message,
            AIMessage.create(tool_calls=[ToolCall(id="call_2", name="noop")]),
            SystemMessage.create("Answer in English."),
        ],
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    assert transcript.system == "Be brief."
    assert transcript.prompt == (
        "<messages>\n"
        "<human_message>\nWeather?\n</human_message>\n"
        "<ai_message>\nChecking.\n</ai_message>\n"
        '<tool_call id="call_1" name="get_weather">\n{"city": "名古屋"}\n</tool_call>\n'
        '<tool_result id="call_1" name="get_weather" failed="true">\nrain\n</tool_result>\n'
        '<tool_call id="call_2" name="noop">\n{}\n</tool_call>\n'
        "<system_message>\nAnswer in English.\n</system_message>\n"
        "</messages>"
    )
    assert transcript.media_parts == []


async def test_to_transcript_media(
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
    image_file_info: ImageFileInfo,
) -> None:
    transcript = await to_transcript(
        [HumanMessage.create("What is this?", files=[image_file_info])],
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    assert transcript.system is None
    assert transcript.media_parts == [{"type": "image", "mime_type": "image/png"}]
    assert '<attachment index="1" />' in transcript.prompt
    assert "What is this?" in transcript.prompt
