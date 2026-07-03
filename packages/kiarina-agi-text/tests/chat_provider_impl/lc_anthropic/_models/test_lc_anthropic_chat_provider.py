# mypy: ignore-errors

import pytest

from kiarina.agi.chat_provider_impl.lc_anthropic import (
    LCAnthropicChatProvider,
    LCAnthropicChatProviderSettings,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCAIMessage,
    LCHumanMessage,
    LCToolInfo,
)


@pytest.fixture
def provider(capabilities) -> LCAnthropicChatProvider:
    capabilities.output_enabled["image"] = True
    provider = LCAnthropicChatProvider(
        LCAnthropicChatProviderSettings(
            input_enabled=capabilities.input_enabled,
            output_enabled=capabilities.output_enabled,
        )
    )
    provider.name = "lc_anthropic"
    return provider


@pytest.fixture
def ctx(run_context):
    return LangChainChatProviderContext.create(run_context=run_context)


def test_provider(provider: LCAnthropicChatProvider) -> None:
    print(f"__str__: {provider!s}")
    print(f"anthropic_settings: {provider.anthropic_settings}")
    print(f"token_count_limit: {provider.token_count_limit}")


# --------------------------------------------------
# LangChainMediaConverter
# --------------------------------------------------


def test_to_image_content(provider: LCAnthropicChatProvider, image_file_blob):
    content = provider.to_image_content(image_file_blob.mime_blob)
    assert content is not None


def test_to_pdf_content(provider: LCAnthropicChatProvider, pdf_file_blob):
    content = provider.to_pdf_content(
        pdf_file_blob.mime_blob, display_name="sample.pdf"
    )
    assert content is not None


# --------------------------------------------------
# Template Methods (Lifecycle)
# --------------------------------------------------


async def test_pre_request(
    provider: LCAnthropicChatProvider,
    lc_tool_infos: list[LCToolInfo],
    ctx: LangChainChatProviderContext,
) -> None:
    lc_tool_infos = lc_tool_infos.copy()
    lc_tool_infos[-1] = lc_tool_infos[-1].copy()
    lc_tool_infos[-1]["cache_control"] = {"type": "ephemeral"}

    ctx.lc_messages = [
        LCHumanMessage(content="Hello"),
        LCHumanMessage(content=""),
        LCHumanMessage(content=[]),
    ]
    ctx.lc_tool_infos = lc_tool_infos

    ctx = await provider._pre_request(ctx)

    assert len(ctx.lc_messages) == 3
    assert ctx.lc_messages[0].content == "Hello"
    assert ctx.lc_messages[1].content == "<no message>"
    assert ctx.lc_messages[2].content == "<no message>"

    assert ctx.lc_tool_infos is not None
    assert len(ctx.lc_tool_infos) == len(lc_tool_infos)
    assert ctx.lc_tool_infos[-1].get("cache_control") is not None


async def test_post_request(
    provider: LCAnthropicChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    lc_ai_message = await provider._post_request(
        ctx,
        LCAIMessage(content=[{"type": "tool_use"}]),
    )

    assert len(lc_ai_message.content) == 0


# --------------------------------------------------
# Template Methods (Invocation)
# --------------------------------------------------


@pytest.mark.costly
async def test_invoke(
    provider: LCAnthropicChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)
    print(lc_ai_message.model_dump_json(indent=2))
    print(lc_ai_message.text())


@pytest.mark.costly
async def test_stream(
    provider: LCAnthropicChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]

    async for lc_ai_message_chunk in provider._stream(ctx):
        if text := lc_ai_message_chunk.content:
            print(text, end="", flush=True)

    print()


# --------------------------------------------------
# Template Methods (Result Handling)
# --------------------------------------------------


@pytest.mark.costly
@pytest.mark.skip(reason="High cost: run manually when needed.")
async def test_extract_overflow_token_count(
    provider: LCAnthropicChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    provider.settings.model_name = "claude-haiku-4-5-20251001"

    ctx.lc_messages = [
        LCHumanMessage(content="Tell me a long story about AI.\n" * 100_000)
    ]

    try:
        await provider._invoke(ctx)
        raise AssertionError("Expected an exception due to max token limit.")

    except Exception as e:
        print(f"Caught Exception: {e}")
        overflow_token_count = provider._extract_overflow_token_count(e)
        print(f"Overflow Token Count from Exception: {overflow_token_count}")
        assert overflow_token_count is not None and overflow_token_count > 0


@pytest.mark.costly
async def test_get_cost_record(
    large_text_file_blob,
    provider: LCAnthropicChatProvider,
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
        LCHumanMessage(
            content=[
                {
                    "type": "text",
                    "text": lc_content,
                    "cache_control": {"type": "ephemeral"},
                },
            ]
        ),
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
    print("Cost Record:", cost_record)

    assert cost_record is not None
    assert cost_record.microdollars > 0
    assert cost_record.metadata.get("cached_input_tokens", 0) > 0


@pytest.mark.costly
async def test_is_safety_error(
    provider: LCAnthropicChatProvider,
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
    provider: LCAnthropicChatProvider,
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
async def test_tool_calls(
    lc_tool_infos,
    provider: LCAnthropicChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [LCHumanMessage(content="Hello")]
    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage:", lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print("LCAIMessage.content:", lc_ai_message.content)
    print("LCAIMessage.tool_calls:", lc_ai_message.tool_calls)


@pytest.mark.costly
async def test_parallel_tool_calls(
    lc_tool_infos,
    provider: LCAnthropicChatProvider,
    ctx: LangChainChatProviderContext,
) -> None:
    ctx.lc_messages = [
        LCHumanMessage(content="Tell me the current weather and news."),
    ]
    ctx.lc_tool_infos = lc_tool_infos
    ctx.tool_choice = "any"
    ctx.parallel_tool_calls = True

    lc_ai_message = await provider._invoke(ctx)

    print("LCAIMessage:", lc_ai_message.model_dump_json(exclude={"content"}, indent=2))
    print("LCAIMessage.content:", lc_ai_message.content)
    print("LCAIMessage.tool_calls:", lc_ai_message.tool_calls)
