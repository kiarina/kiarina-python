import asyncio

from _common import configure_script

from kiarina.agi.chat_provider import TokenOverflowError
from kiarina.agi.chat_provider_impl.anthropic import (
    AnthropicChatProvider,
    AnthropicChatProviderSettings,
)
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.message import HumanMessage


async def main() -> None:
    run_context = configure_script()
    provider = AnthropicChatProvider(
        AnthropicChatProviderSettings(model_name="claude-haiku-4-5-20251001")
    )
    provider.name = "anthropic"

    try:
        async for _ in provider.run(
            [HumanMessage.create("Tell me a long story about AI.\n" * 100_000)],
            cost_recorder=NullCostRecorder(),
            run_context=run_context,
        ):
            pass
    except TokenOverflowError as error:
        print(f"Overflow Token Count: {error.token_count}")
        if error.token_count <= 0:
            raise AssertionError("Failed to extract overflow token count.") from error
        return

    raise AssertionError("Expected a TokenOverflowError.")


if __name__ == "__main__":
    asyncio.run(main())
