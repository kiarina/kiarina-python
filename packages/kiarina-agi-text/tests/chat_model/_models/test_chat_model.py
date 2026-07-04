from typing import Any

from kiarina.agi.chat_model import chat_model_registry
from kiarina.agi.chat_provider_impl.mock import MockChatProvider


def test_chat_model() -> None:
    chat_model = chat_model_registry.resolve("mock")
    assert chat_model.provider_name == "mock"
    assert chat_model.provider_config["token_count_limit"] == 100_000
    assert chat_model.get_capabilities().is_supported("text") is True
    assert chat_model.token_scale_factor == 1.0
    assert isinstance(chat_model.provider, MockChatProvider)
    print("__str__:", str(chat_model))


async def test_run(messages: Any, run_context: Any) -> None:
    chat_model = chat_model_registry.resolve("mock")

    ai_messages = [
        ai_message
        async for ai_message in chat_model.run(
            messages,
            streaming=False,
            run_context=run_context,
        )
    ]

    assert len(ai_messages) == 1
    print("AI Message:", ai_messages[0])
