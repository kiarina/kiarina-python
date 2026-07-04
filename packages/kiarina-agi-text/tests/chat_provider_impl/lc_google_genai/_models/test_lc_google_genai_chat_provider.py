# mypy: ignore-errors

import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.lc_google_genai import (
    LCGoogleGenAIChatProvider,
    LCGoogleGenAIChatProviderSettings,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCHumanMessage,
)
from kiarina.utils.file import FileBlob


@pytest.fixture
def capabilities() -> ChatCapabilities:
    return ChatCapabilities(
        input_enabled={
            "image": True,
            "audio": True,
            "video": True,
            "pdf": True,
        },
    )


@pytest.fixture
def provider_gemini_api(capabilities) -> LCGoogleGenAIChatProvider:
    provider = LCGoogleGenAIChatProvider(
        LCGoogleGenAIChatProviderSettings(
            backend_type="gemini_api",
            google_auth_settings_key="api_key",
            input_enabled=capabilities.input_enabled,
            output_enabled=capabilities.output_enabled,
        )
    )
    provider.name = "lc_google_genai"
    return provider


@pytest.fixture
def provider_vertex_ai_api_key(capabilities) -> LCGoogleGenAIChatProvider:
    provider = LCGoogleGenAIChatProvider(
        LCGoogleGenAIChatProviderSettings(
            backend_type="vertex_ai_api_key",
            google_auth_settings_key="api_key",
            input_enabled=capabilities.input_enabled,
            output_enabled=capabilities.output_enabled,
        )
    )
    provider.name = "lc_google_genai"
    return provider


@pytest.fixture
def provider_vertex_ai_credentials(capabilities) -> LCGoogleGenAIChatProvider:
    provider = LCGoogleGenAIChatProvider(
        LCGoogleGenAIChatProviderSettings(
            backend_type="vertex_ai_credentials",
            google_auth_settings_key="service_account",
            input_enabled=capabilities.input_enabled,
            output_enabled=capabilities.output_enabled,
        )
    )
    provider.name = "lc_google_genai"
    return provider


@pytest.fixture
def provider(provider_gemini_api) -> LCGoogleGenAIChatProvider:
    return provider_gemini_api


@pytest.fixture
def ctx(run_context):
    return LangChainChatProviderContext.create(run_context=run_context)


# --------------------------------------------------
# Backend
# --------------------------------------------------


@pytest.mark.costly
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("provider_gemini_api", id="1. gemini_api"),
        # pytest.param("provider_vertex_ai_api_key", id="2. vertex_ai_api_key"),
        pytest.param("provider_vertex_ai_credentials", id="3. vertex_ai_credentials"),
    ],
)
async def test_backend(
    fixture_name, request, ctx: LangChainChatProviderContext
) -> None:
    print("\n\n" + "=" * 10 + f" {fixture_name} " + "=" * 10 + "\n")

    provider: LCGoogleGenAIChatProvider = request.getfixturevalue(fixture_name)
    print(f"__str__: {provider!s}")
    print(f"google_auth_settings: {provider.google_auth_settings}")
    print(f"backend_config: {provider.backend_config}")

    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage", lc_ai_message.model_dump_json(indent=2))
    print("LCAIMessage.text()", lc_ai_message.text())


# --------------------------------------------------
# Methods (LangChainMediaConverter)
# --------------------------------------------------


def test_to_image_content(
    image_file_blob: FileBlob,
    provider: LCGoogleGenAIChatProvider,
) -> None:
    content = provider.to_image_content(image_file_blob.mime_blob)
    assert content is not None


def test_to_audio_content(
    audio_file_blob: FileBlob,
    provider: LCGoogleGenAIChatProvider,
) -> None:
    content = provider.to_audio_content(audio_file_blob.mime_blob)
    assert content is not None


def test_to_video_content(
    video_file_blob: FileBlob,
    provider: LCGoogleGenAIChatProvider,
) -> None:
    content = provider.to_video_content(video_file_blob.mime_blob)
    assert content is not None


def test_to_pdf_content(
    pdf_file_blob: FileBlob,
    provider: LCGoogleGenAIChatProvider,
) -> None:
    content = provider.to_pdf_content(
        pdf_file_blob.mime_blob, display_name="sample.pdf"
    )
    assert content is not None


# --------------------------------------------------
# Template Methods (Invocation)
# --------------------------------------------------


@pytest.mark.costly
async def test_invoke(
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage", lc_ai_message.model_dump_json(indent=2))
    print("LCAIMessage.text()", lc_ai_message.text())


@pytest.mark.costly
async def test_stream(
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]

    async for lc_ai_message_chunk in provider._stream(ctx):
        if text := lc_ai_message_chunk.text():
            print(text, end="", flush=True)

    print()


# --------------------------------------------------
# Template Methods (Result Handling)
# --------------------------------------------------


@pytest.mark.costly
async def test_get_cost_record(
    large_text_file_blob: FileBlob,
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    lc_content = (
        f"<files>"
        f'<file file_path="{large_text_file_blob.file_path}">'
        f"{large_text_file_blob.raw_text}"
        f"</file>"
        f"</files>"
    )

    ctx.lc_messages = [
        LCHumanMessage(content=lc_content),
        LCHumanMessage(content="Hello, how are you?"),
    ]

    lc_ai_message = await provider._invoke(ctx)
    cost_record = provider._get_cost_record(lc_ai_message)

    print("---- LCAIMessage ----")
    print(lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(lc_ai_message.content)
    print("Cost Record:", cost_record)

    assert cost_record is not None
    assert cost_record.microdollars > 0.0

    ctx.lc_messages.append(lc_ai_message)
    ctx.lc_messages.append(LCHumanMessage(content="Tell me a joke."))

    lc_ai_message = await provider._invoke(ctx)
    cost_record = provider._get_cost_record(lc_ai_message)

    print("---- LCAIMessage ----")
    print(lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(lc_ai_message.content)
    print("Cost Record:", cost_record)

    assert cost_record is not None
    assert cost_record.microdollars > 0.0


@pytest.mark.costly
async def test_is_safety_error(
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)

    print("---- LCAIMessage ----")
    print(lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(lc_ai_message.content)

    assert provider._is_safety_error(lc_ai_message) is False


@pytest.mark.costly
async def test_is_max_token_error(
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    provider.settings.max_output_tokens = 50
    ctx.lc_messages = [LCHumanMessage(content="Tell me a story about AI.")]
    lc_ai_message = await provider._invoke(ctx)

    print("---- LCAIMessage ----")
    print(lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(lc_ai_message.content)

    assert provider._is_max_token_error(lc_ai_message) is True


# --------------------------------------------------
# Use Cases
# --------------------------------------------------


@pytest.mark.costly
async def test_tool_calls(
    lc_tool_infos,
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    ctx.lc_tool_infos = lc_tool_infos
    ctx.tool_choice = "any"
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage:", lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print("LCAIMessage.content:", lc_ai_message.content)
    print("LCAIMessage.tool_calls:", lc_ai_message.tool_calls)


@pytest.mark.costly
async def test_parallel_tool_calls(
    lc_tool_infos,
    provider: LCGoogleGenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Tell me the current weather and news.")]
    ctx.lc_tool_infos = lc_tool_infos
    ctx.tool_choice = "any"
    ctx.parallel_tool_calls = True
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage:", lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print("LCAIMessage.content:", lc_ai_message.content)
    print("LCAIMessage.tool_calls:", lc_ai_message.tool_calls)
