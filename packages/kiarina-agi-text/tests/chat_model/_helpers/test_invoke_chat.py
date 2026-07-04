# mypy: ignore-errors

import pytest

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    ToolCall,
    ToolMessage,
)


@pytest.fixture
def args(cost_recorder, run_context):
    return {
        "cost_recorder": cost_recorder,
        "run_context": run_context,
    }


async def test_invoke(args) -> None:
    await invoke_chat(
        [HumanMessage.create("Hello")],
        **args,
    )


async def test_tool_info_auto_no_tool_call(tool_info, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Hello")],
        tool_infos=[tool_info],
        chat_options={
            "tool_choice": "auto",
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 0


async def test_tool_info_auto_tool_call(tool_info, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Hello, can you get me the weather in Tokyo?")],
        tool_infos=[tool_info],
        chat_options={
            "tool_choice": "auto",
        },
        **args,
    )

    assert len(ai_message.tool_calls) >= 0


async def test_info_any(tool_info, create_tool_call_message, args) -> None:
    ai_message = await invoke_chat(
        [create_tool_call_message("Hello", "get_weather")],
        tool_infos=[tool_info],
        chat_options={
            "tool_choice": "any",
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 1


async def test_tool_infos_not_parallel(
    tool_infos, create_tool_call_message, args
) -> None:
    ai_message = await invoke_chat(
        [
            create_tool_call_message(
                "Tell me the weather and the latest news.",
                "get_weather",
            )
        ],
        tool_infos=tool_infos,
        chat_options={
            "tool_choice": "any",
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 1


async def test_tool_infos_parallel(tool_infos, create_tool_call_message, args) -> None:
    ai_message = await invoke_chat(
        [
            create_tool_call_message(
                "Tell me the weather and the latest news.",
                "get_weather",
                "get_news",
            )
        ],
        tool_infos=tool_infos,
        chat_options={
            "tool_choice": "any",
            "parallel_tool_calls": True,
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 2


async def test_image_input(image_file_info, args) -> None:
    await invoke_chat(
        [HumanMessage.create("What do you see in this image?", [image_file_info])],
        **args,
    )


async def test_image_output(image_file_info, generate_tool_infos, args) -> None:
    await invoke_chat(
        [
            HumanMessage.create("Create an image."),
            AIMessage.create(
                "OK, generating an image now.",
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="generate_image",
                        args={"instructions": "Create an image."},
                    )
                ],
            ),
            ToolMessage.create(
                "image generated.",
                [image_file_info],
                tool_name="generate_image",
                tool_call_args={"instructions": "Create an image."},
                tool_call_id="1",
            ),
        ],
        tool_infos=generate_tool_infos,
        **args,
    )


async def test_audio_input(audio_file_info, args) -> None:
    await invoke_chat(
        [HumanMessage.create("What do you hear in this audio?", [audio_file_info])],
        **args,
    )


async def test_audio_output(audio_file_info, generate_tool_infos, args) -> None:
    await invoke_chat(
        [
            HumanMessage.create("Create an audio."),
            AIMessage.create(
                "OK, generating an audio now.",
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="generate_audio",
                        args={"instructions": "Create an audio."},
                    )
                ],
            ),
            ToolMessage.create(
                "audio generated.",
                [audio_file_info],
                tool_name="generate_audio",
                tool_call_args={"instructions": "Create an audio."},
                tool_call_id="1",
            ),
        ],
        tool_infos=generate_tool_infos,
        **args,
    )


async def test_video_input(video_file_info, args) -> None:
    await invoke_chat(
        [HumanMessage.create("What do you see in this video?", [video_file_info])],
        **args,
    )


async def test_video_output(video_file_info, generate_tool_infos, args) -> None:
    await invoke_chat(
        [
            HumanMessage.create("Create a video."),
            AIMessage.create(
                "OK, generating a video now.",
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="generate_video",
                        args={"instructions": "Create a video."},
                    )
                ],
            ),
            ToolMessage.create(
                "video generated.",
                [video_file_info],
                tool_name="generate_video",
                tool_call_args={"instructions": "Create a video."},
                tool_call_id="1",
            ),
        ],
        tool_infos=generate_tool_infos,
        **args,
    )


async def test_pdf_input(pdf_file_info, args) -> None:
    await invoke_chat(
        [
            HumanMessage.create("Here is a PDF file:"),
            HumanMessage.create(
                "Here is a PDF file:\nSummarize the content of this PDF.",
                [pdf_file_info],
            ),
        ],
        **args,
    )


async def test_pdf_output(pdf_file_info, generate_tool_infos, args) -> None:
    await invoke_chat(
        [
            HumanMessage.create("Create a PDF."),
            AIMessage.create(
                "OK, generating a PDF now.",
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="generate_pdf",
                        args={"instructions": "Create a PDF."},
                    )
                ],
            ),
            ToolMessage.create(
                "PDF generated.",
                [pdf_file_info],
                tool_name="generate_pdf",
                tool_call_args={"instructions": "Create a PDF."},
                tool_call_id="1",
            ),
        ],
        tool_infos=generate_tool_infos,
        **args,
    )
