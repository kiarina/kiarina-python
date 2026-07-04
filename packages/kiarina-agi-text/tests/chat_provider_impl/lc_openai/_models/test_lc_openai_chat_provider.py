# mypy: ignore-errors

import pytest

from kiarina.agi.chat_provider_impl.lc_openai import (
    LCOpenAIChatProvider,
    LCOpenAIChatProviderSettings,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCAIMessage,
    LCHumanMessage,
    LCMessage,
)
from kiarina.utils.file import FileBlob


@pytest.fixture
def provider(capabilities) -> LCOpenAIChatProvider:
    provider = LCOpenAIChatProvider(
        LCOpenAIChatProviderSettings(
            input_enabled=capabilities.input_enabled,
            output_enabled=capabilities.output_enabled,
        )
    )
    provider.name = "lc_openai"
    return provider


def test_get_capabilities() -> None:
    provider = LCOpenAIChatProvider(
        LCOpenAIChatProviderSettings(
            context_window=4096,
            max_output_tokens=1024,
            token_count_limit=2048,
            input_enabled={"image": True},
        )
    )

    capabilities = provider.get_capabilities()

    assert capabilities.token_count_limit == 2048
    assert capabilities.can_include("human", "image")
    assert not capabilities.can_include("human", "pdf")


def test_get_capabilities_use_settings_token_count_limit_default() -> None:
    provider = LCOpenAIChatProvider(
        LCOpenAIChatProviderSettings(
            context_window=4096,
            max_output_tokens=1024,
            input_enabled={"image": True},
        )
    )

    capabilities = provider.get_capabilities()

    assert capabilities.token_count_limit == 272_000


@pytest.fixture
def ctx(run_context):
    return LangChainChatProviderContext.create(run_context=run_context)


@pytest.fixture
def lc_messages_with_pdf(provider, pdf_file_blob) -> list[LCMessage]:
    return [
        LCHumanMessage(
            content=[
                "Look at this file",
                provider.to_pdf_content(
                    pdf_file_blob.mime_blob, display_name="sample.pdf"
                ),
            ]
        )
    ]


def test_provider(provider: LCOpenAIChatProvider):
    print(f"__str__: {provider!s}")
    print(f"openai_settings: {provider.openai_settings}")


# --------------------------------------------------
# LangChainMediaConverter
# --------------------------------------------------


def test_to_image_content(provider: LCOpenAIChatProvider, image_file_blob):
    content = provider.to_image_content(image_file_blob.mime_blob)
    assert content is not None


def test_to_pdf_content(provider: LCOpenAIChatProvider, pdf_file_blob):
    content = provider.to_pdf_content(
        pdf_file_blob.mime_blob, display_name="sample.pdf"
    )
    assert content is not None


# --------------------------------------------------
# Template Methods (Lifecycle)
# --------------------------------------------------


async def test_pre_request_responses_api(
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
    lc_messages_with_pdf,
) -> None:
    ctx.lc_messages = lc_messages_with_pdf
    await provider._pre_request(ctx)
    assert provider.use_responses_api is True


async def test_pre_request_chat_completions_api(
    lc_messages,
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = lc_messages
    await provider._pre_request(ctx)
    assert provider.use_responses_api is False


async def test_post_request(
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    lc_ai_message = await provider._post_request(
        ctx,
        LCAIMessage(
            content=[
                {"type": "reasoning"},
                {"type": "text", "text": "This is a response."},
            ]
        ),
    )

    assert lc_ai_message.content == "This is a response."


# --------------------------------------------------
# Template Methods (Invocation)
# --------------------------------------------------


@pytest.mark.costly
async def test_invoke(
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    provider.use_responses_api = True
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)

    print(lc_ai_message.model_dump_json(indent=2))
    print(lc_ai_message.content)


@pytest.mark.costly
async def test_stream(
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    provider.use_responses_api = True
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
    provider: LCOpenAIChatProvider,
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
    assert cost_record.microdollars > 0

    ctx.lc_messages.append(lc_ai_message)
    ctx.lc_messages.append(LCHumanMessage(content="Tell me a joke."))

    lc_ai_message = await provider._invoke(ctx)
    cost_record = provider._get_cost_record(lc_ai_message)

    print("---- LCAIMessage ----")
    print(lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(lc_ai_message.content)

    assert cost_record is not None
    assert cost_record.microdollars > 0
    assert cost_record.metadata.get("cached_input_tokens", 0) > 0


@pytest.mark.costly
async def test_is_safety_error(
    provider: LCOpenAIChatProvider,
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
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    provider.settings.max_output_tokens = 50
    ctx.lc_messages = [LCHumanMessage(content="Tell me a long story about AI.")]
    lc_ai_message = await provider._invoke(ctx)

    print("---- LCAIMessage ----")
    print(lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(lc_ai_message.content)

    assert provider._is_max_token_error(lc_ai_message) is True


# --------------------------------------------------
# Use Cases
# --------------------------------------------------


@pytest.mark.costly
async def test_reasoning_effort_and_verbosity(
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    provider.settings.endpoint_type = "responses"
    provider.settings.reasoning_effort = "medium"
    provider.settings.verbosity = "medium"
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage:", lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print("LCAIMessage.content:", lc_ai_message.content)


@pytest.mark.costly
async def test_tool_calls(
    lc_tool_infos,
    provider: LCOpenAIChatProvider,
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
    provider: LCOpenAIChatProvider,
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


@pytest.mark.costly
async def test_parallel_tool_calls_order(
    provider: LCOpenAIChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    from pydantic import BaseModel

    class WriteFile(BaseModel):
        """Write text to a file."""

        file_path: str
        text: str

    class CatFile(BaseModel):
        """Read the content of a file."""

        file_path: str

    from kiarina.agi.tool_info import create_tool_info

    tool_infos = [
        create_tool_info(WriteFile),
        create_tool_info(CatFile),
    ]

    from kiarina.agi.langchain_chat_provider import from_tool_infos

    lc_tool_infos = from_tool_infos(tool_infos)

    ctx.lc_messages = [
        LCHumanMessage(
            content="./hello.txt に Hello と書いて、./hello.txt を CatFile して"
        ),
    ]
    ctx.lc_tool_infos = lc_tool_infos
    ctx.tool_choice = "any"
    ctx.parallel_tool_calls = True
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage:", lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print("LCAIMessage.content:", lc_ai_message.content)
    print("LCAIMessage.tool_calls:", lc_ai_message.tool_calls)
