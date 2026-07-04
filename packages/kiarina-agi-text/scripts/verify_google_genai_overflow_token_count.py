import asyncio

from _common import configure_script

from kiarina.agi.chat_provider_impl.lc_google_genai import (
    LCGoogleGenAIChatProvider,
    LCGoogleGenAIChatProviderSettings,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCHumanMessage,
)


async def main() -> None:
    run_context = configure_script()
    provider = LCGoogleGenAIChatProvider(LCGoogleGenAIChatProviderSettings())
    context = LangChainChatProviderContext.create(run_context=run_context)
    context.lc_messages = [
        LCHumanMessage(content="Tell me a long story about AI.\n" * 200_000)
    ]

    try:
        await provider._invoke(context)
    except Exception as error:
        print(f"Caught Exception: {error}")
        overflow_token_count = provider._extract_overflow_token_count(error)
        print(f"Overflow Token Count from Exception: {overflow_token_count}")
        if overflow_token_count is None:
            raise AssertionError("Failed to extract overflow token count.") from error
        return

    raise AssertionError("Expected an exception due to max token limit.")


if __name__ == "__main__":
    asyncio.run(main())
