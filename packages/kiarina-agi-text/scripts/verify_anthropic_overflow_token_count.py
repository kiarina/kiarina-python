import asyncio

from _common import configure_script

from kiarina.agi.chat_provider_impl.lc_anthropic import (
    LCAnthropicChatProvider,
    LCAnthropicChatProviderSettings,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCHumanMessage,
)


async def main() -> None:
    run_context = configure_script()
    provider = LCAnthropicChatProvider(
        LCAnthropicChatProviderSettings(model_name="claude-haiku-4-5-20251001")
    )
    context = LangChainChatProviderContext.create(run_context=run_context)
    context.lc_messages = [
        LCHumanMessage(content="Tell me a long story about AI.\n" * 100_000)
    ]

    try:
        await provider._invoke(context)
    except Exception as error:
        print(f"Caught Exception: {error}")
        overflow_token_count = provider._extract_overflow_token_count(error)
        print(f"Overflow Token Count from Exception: {overflow_token_count}")
        if overflow_token_count is None or overflow_token_count <= 0:
            raise AssertionError("Failed to extract overflow token count.") from error
        return

    raise AssertionError("Expected an exception due to max token limit.")


if __name__ == "__main__":
    asyncio.run(main())
