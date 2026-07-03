# mypy: ignore-errors

import pytest

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.tool_info import ToolInfo

pytestmark = [pytest.mark.costly]


@pytest.fixture
def args(cost_recorder, run_context):
    return {
        "cost_recorder": cost_recorder,
        "run_context": run_context,
    }


async def test_invoke(chat_model_name, args) -> None:
    await invoke_chat(
        [HumanMessage.create("Hello")],
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_tool_info_auto_no_tool_call(chat_model_name, tool_info, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Hello")],
        tool_infos=[tool_info],
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "auto",
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 0


async def test_tool_info_auto_tool_call(chat_model_name, tool_info, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Hello, can you get me the weather in Tokyo?")],
        tool_infos=[tool_info],
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "auto",
        },
        **args,
    )

    assert len(ai_message.tool_calls) >= 0


async def test_info_any(chat_model_name, tool_info, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Hello")],
        tool_infos=[tool_info],
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "any",
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 1


async def test_tool_infos_not_parallel(chat_model_name, tool_infos, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Tell me the weather and the latest news.")],
        tool_infos=tool_infos,
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "any",
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 1


async def test_tool_infos_parallel(chat_model_name, tool_infos, args) -> None:
    ai_message = await invoke_chat(
        [HumanMessage.create("Tell me the weather and the latest news.")],
        tool_infos=tool_infos,
        chat_options={
            "chat_model": chat_model_name,
            "tool_choice": "any",
            "parallel_tool_calls": True,
        },
        **args,
    )

    assert len(ai_message.tool_calls) == 2


async def test_image_input(chat_model_name, image_file_info, args) -> None:
    await invoke_chat(
        [HumanMessage.create("What do you see in this image?", [image_file_info])],
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_image_output(
    chat_model_name, image_file_info, generate_tool_infos, args
) -> None:
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
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_audio_input(chat_model_name, audio_file_info, args) -> None:
    await invoke_chat(
        [HumanMessage.create("What do you hear in this audio?", [audio_file_info])],
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_audio_output(
    chat_model_name, audio_file_info, generate_tool_infos, args
) -> None:
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
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_video_input(chat_model_name, video_file_info, args) -> None:
    await invoke_chat(
        [HumanMessage.create("What do you see in this video?", [video_file_info])],
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_video_output(
    chat_model_name, video_file_info, generate_tool_infos, args
) -> None:
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
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_pdf_input(chat_model_name, pdf_file_info, args) -> None:
    await invoke_chat(
        [
            HumanMessage.create("Here is a PDF file:"),
            HumanMessage.create(
                "Here is a PDF file:\nSummarize the content of this PDF.",
                [pdf_file_info],
            ),
        ],
        chat_options={"chat_model": chat_model_name},
        **args,
    )


async def test_pdf_output(
    chat_model_name, pdf_file_info, generate_tool_infos, args
) -> None:
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
        chat_options={"chat_model": chat_model_name},
        **args,
    )


@pytest.mark.skip(reason="High cost: run manually when needed.")
async def test_content_cache(
    chat_model_name, large_text_file_blob, args, disable_request_logger
) -> None:
    # OpenAI is automatically cached.
    # Anthropic requires explicit cache specification for Content
    # Google's implicit cache behaviour is unclear; explicit caching is heavy and therefore not used.
    content = (
        f"<files>"
        f'<file  file_path="{large_text_file_blob.file_path}">'
        f"{large_text_file_blob.raw_text}"
        f"</file>"
        f"</files>"
    )

    from kiarina.agi.content import Content

    messages: list[Message] = [
        HumanMessage(
            contents=[
                Content(
                    text=content,
                    cache_control={"type": "ephemeral"},
                )
            ]
        ),
        HumanMessage.create("Hello, how are you?"),
    ]

    print("=" * 20 + " AIMessage 1/2 " + "=" * 20)

    ai_message = await invoke_chat(
        messages,
        chat_options={
            "chat_model": chat_model_name,
        },
        **args,
    )

    messages.append(ai_message)
    messages.append(HumanMessage.create("Tell me a joke."))

    print("=" * 20 + " AIMessage 2/2 " + "=" * 20)

    await invoke_chat(
        messages,
        chat_options={
            "chat_model": chat_model_name,
        },
        **args,
    )


@pytest.mark.skip(reason="High cost: run manually when needed.")
async def test_tool_cache(
    chat_model_name, large_tool_infos, args, disable_request_logger
) -> None:
    # OpenAI automatically caches tools as well.
    # Anthropic requires explicit cache specifications for its tools.
    # Google does not cache tools.

    # Specifying caching for Anthropic tools does not cause errors with OpenAI or Google.
    large_tool_infos[-1]["cache_control"] = {"type": "ephemeral"}

    print("=" * 20 + " Tool Infos " + "=" * 20)
    print("last tool:", large_tool_infos[-1])

    messages: list[Message] = [
        HumanMessage.create("Hello, how are you?"),
    ]

    print("=" * 20 + " AIMessage 1/2 " + "=" * 20)

    ai_message = await invoke_chat(
        messages,
        tool_infos=large_tool_infos,
        chat_options={"chat_model": chat_model_name},
        **args,
    )

    messages.append(ai_message)
    messages.append(
        HumanMessage.create("Please provide the latest information on the OpenAI API.")
    )

    print("=" * 20 + " AIMessage 2/2 " + "=" * 20)

    await invoke_chat(
        messages,
        tool_infos=large_tool_infos,
        chat_options={"chat_model": chat_model_name},
        **args,
    )


@pytest.mark.skip(reason="Tmp test for recent edits")
async def test_tmp(chat_model_name, args) -> None:
    await invoke_chat(
        [HumanMessage.create("どれが一番好き?")],
        tool_infos=[
            ToolInfo(name=key, description=value)
            for key, value in {
                "apple": "りんごが一番好きです",
                "banana": "バナナが一番好きです",
                "grape": "ぶどうが一番好きです",
            }.items()
        ],
        chat_options={  # type: ignore
            "chat_model": chat_model_name,
            "tool_choice": "any",
        },
        **args,
    )


@pytest.mark.skip(reason="Tmp test for recent edits")
async def test_system_message(chat_model_name, args) -> None:
    from datetime import datetime

    from kiarina.agi.content import Content
    from kiarina.agi.message import SystemMessage

    await invoke_chat(
        [
            SystemMessage(
                contents=[
                    Content(
                        text=(
                            "あなたは時間によって好きな果物が変わる人です。"
                            "現在時刻の分が奇数のときはりんごが好きで、偶数のときはバナナが好きです。"
                            "ただし、30秒〜59秒の間は例外としてぶどうが好きです。"
                        ),
                    ),
                    Content(
                        text=f"現在の時刻は{datetime.now().strftime('%H:%M:%S')}です。",
                    ),
                ],
            ),
            HumanMessage.create("どれが一番好き?"),
        ],
        tool_infos=[
            ToolInfo(name=key, description=value)
            for key, value in {
                "apple": "りんごが一番好きです",
                "banana": "バナナが一番好きです",
                "grape": "ぶどうが一番好きです",
            }.items()
        ],
        chat_options={  # type: ignore
            "chat_model": chat_model_name,
            "tool_choice": "any",
        },
        **args,
    )


@pytest.mark.skip(reason="Tmp test for recent edits")
async def test_ai_message_continuation(chat_model_name, args) -> None:
    # OpenAI: 連続の AIMessage, HumanMessage のない AIMessage を許容
    # Anthropic: 連続の AIMessage を許容しない, HumanMessage のない AIMessage を許容しない
    # Google: 連続の AIMessage を許容, HumanMessage のない AIMessage を許容
    await invoke_chat(
        [
            HumanMessage.create("こんにちは。"),
            AIMessage.create("最初の回答です。"),
            AIMessage.create("続けて回答します。"),
        ],
        chat_options={
            "chat_model": chat_model_name,
        },
        **args,
    )
