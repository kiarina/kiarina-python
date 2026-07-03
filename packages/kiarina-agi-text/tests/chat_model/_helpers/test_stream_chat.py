# mypy: ignore-errors

import pytest

from kiarina.agi.chat_model import stream_chat
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    ToolCall,
    ToolMessage,
)

pytestmark = [pytest.mark.costly]


@pytest.fixture
def args(cost_recorder, run_context):
    return {
        "cost_recorder": cost_recorder,
        "run_context": run_context,
    }


async def test_stream(chat_model_name, args) -> None:
    async for _ in stream_chat(
        [HumanMessage.create("Hello")],
        chat_options={
            "chat_model": chat_model_name,
        },
        **args,
    ):
        pass


async def test_tool_info_auto_no_tool_call(chat_model_name, tool_info, args) -> None:
    ai_message = None
    async for generated_message in stream_chat(
        [HumanMessage.create("Hello")],
        tool_infos=[tool_info],
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "auto",
        },
        **args,
    ):
        ai_message = generated_message

    assert len(ai_message.tool_calls) == 0


async def test_tool_info_auto_tool_call(chat_model_name, tool_info, args) -> None:
    message = None
    async for generated_message in stream_chat(
        [HumanMessage.create("Hello, can you get me the weather in Tokyo?")],
        tool_infos=[tool_info],
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "auto",
        },
        **args,
    ):
        message = generated_message

    assert len(message.tool_calls) >= 0


async def test_info_any(chat_model_name, tool_info, args) -> None:
    message = None
    async for generated_message in stream_chat(
        [HumanMessage.create("Hello")],
        tool_infos=[tool_info],
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "any",
        },
        **args,
    ):
        message = generated_message

    assert len(message.tool_calls) == 1


async def test_tool_infos_not_parallel(chat_model_name, tool_infos, args) -> None:
    message = None
    async for generated_message in stream_chat(
        [HumanMessage.create("Tell me the weather and the latest news.")],
        tool_infos=tool_infos,
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "any",
        },
        **args,
    ):
        message = generated_message

    assert len(message.tool_calls) == 1


async def test_tool_infos_parallel(chat_model_name, tool_infos, args) -> None:
    message = None
    async for generated_message in stream_chat(
        [HumanMessage.create("Tell me the weather and the latest news.")],
        tool_infos=tool_infos,
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "any",
            "parallel_tool_calls": True,
        },
        **args,
    ):
        message = generated_message

    assert len(message.tool_calls) == 2


async def test_image_input(chat_model_name, image_file_info, args) -> None:
    async for _ in stream_chat(
        [HumanMessage.create("What do you see in this image?", [image_file_info])],
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_image_output(
    chat_model_name, image_file_info, generate_tool_infos, args
) -> None:
    async for _ in stream_chat(
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
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_audio_input(chat_model_name, audio_file_info, args) -> None:
    async for _ in stream_chat(
        [HumanMessage.create("What do you hear in this audio?", [audio_file_info])],
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_audio_output(
    chat_model_name, audio_file_info, generate_tool_infos, args
) -> None:
    async for _ in stream_chat(
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
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_video_input(chat_model_name, video_file_info, args) -> None:
    async for _ in stream_chat(
        [HumanMessage.create("What do you see in this video?", [video_file_info])],
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_video_output(
    chat_model_name, video_file_info, generate_tool_infos, args
) -> None:
    async for _ in stream_chat(
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
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_pdf_input(chat_model_name, pdf_file_info, args) -> None:
    async for _ in stream_chat(
        [
            HumanMessage.create("Here is a PDF file:"),
            HumanMessage.create(
                "Here is a PDF file:\nSummarize the content of this PDF.",
                [pdf_file_info],
            ),
        ],
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass


async def test_pdf_output(
    chat_model_name, pdf_file_info, generate_tool_infos, args
) -> None:
    async for _ in stream_chat(
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
        chat_options={"chat_model": chat_model_name},
        **args,
    ):
        pass
