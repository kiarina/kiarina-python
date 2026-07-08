import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.lc_anthropic_vertex import (
    LCAnthropicVertexChatProvider,
    LCAnthropicVertexChatProviderSettings,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCHumanMessage,
    LCToolInfo,
    LCToolMessage,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


@pytest.fixture
def provider(capabilities: ChatCapabilities) -> LCAnthropicVertexChatProvider:
    capabilities.output_enabled["image"] = True
    provider = LCAnthropicVertexChatProvider(
        LCAnthropicVertexChatProviderSettings(
            input_enabled=capabilities.input_enabled,
            output_enabled=capabilities.output_enabled,
        )
    )
    provider.name = "lc_anthropic_vertex"
    return provider


@pytest.fixture
def ctx(run_context: RunContext) -> LangChainChatProviderContext:
    return LangChainChatProviderContext.create(run_context=run_context)


def test_provider(provider: LCAnthropicVertexChatProvider) -> None:
    print(f"__str__: {provider!s}")


# --------------------------------------------------
# LangChainMediaConverter
# --------------------------------------------------


def test_to_image_content(
    provider: LCAnthropicVertexChatProvider,
    image_file_blob: FileBlob,
) -> None:
    content = provider.to_image_content(image_file_blob.mime_blob)
    assert content is not None


# --------------------------------------------------
# Template Methods (Lifecycle)
# --------------------------------------------------


async def test_pre_request(
    image_file_blob: FileBlob,
    provider: LCAnthropicVertexChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    image_file_content = provider.to_image_content(image_file_blob.mime_blob)
    assert image_file_content is not None
    assert image_file_content.get("type") == "image_url"

    ctx.lc_messages = [
        LCHumanMessage(content="Hello"),
        LCHumanMessage(content=""),
        LCHumanMessage(content=[]),
        LCToolMessage(
            content=[
                image_file_content,
                {"type": "text", "text": "Describe the image."},
            ],
            tool_call_id="1",
        ),
    ]
    ctx = await provider._pre_request(ctx)

    assert len(ctx.lc_messages) == 4
    assert ctx.lc_messages[0].content == "Hello"
    assert ctx.lc_messages[1].content == "<no message>"
    assert ctx.lc_messages[2].content == "<no message>"
    assert isinstance(ctx.lc_messages[3].content[0], dict)
    assert ctx.lc_messages[3].content[0].get("type") == "image"


# --------------------------------------------------
# Template Methods (Invocation)
# --------------------------------------------------


@pytest.mark.costly
async def test_invoke(
    provider: LCAnthropicVertexChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    ai_message = await provider._invoke(ctx)

    print(ai_message.model_dump_json(exclude={"content"}, indent=2))
    print(ai_message.content)


@pytest.mark.costly
async def test_stream(
    provider: LCAnthropicVertexChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]

    async for lc_ai_message_chunk in provider._stream(ctx):
        if text := lc_ai_message_chunk.content:
            print(text)

    print()


# --------------------------------------------------
# Use Cases
# --------------------------------------------------


@pytest.mark.costly
async def test_tool_calls(
    lc_tool_infos: list[LCToolInfo],
    provider: LCAnthropicVertexChatProvider,
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
    lc_tool_infos: list[LCToolInfo],
    provider: LCAnthropicVertexChatProvider,
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
