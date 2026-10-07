from collections.abc import Callable

from anthropic.types import Message

from kiarina.agi.chat_provider_impl.anthropic._operations.from_anthropic_message import (
    from_anthropic_message,
)


def test_from_anthropic_message(make_message: Callable[..., Message]) -> None:
    result = from_anthropic_message(
        make_message(
            [
                {"type": "text", "text": "Hi"},
                {"type": "tool_use", "id": "toolu_1", "name": "f", "input": {"a": 1}},
            ],
            stop_reason="tool_use",
        ),
        cache_ttl="5m",
    )

    assert result.ai_message.contents[0].text == "Hi"
    assert result.ai_message.tool_calls[0].id == "toolu_1"
    assert result.ai_message.tool_calls[0].args == {"a": 1}
    assert result.stop_reason == "stop"
    assert result.usage is not None
    assert result.usage.input_tokens == 10


def test_refusal(make_message: Callable[..., Message]) -> None:
    result = from_anthropic_message(make_message(stop_reason="refusal"), cache_ttl="5m")

    assert result.ai_message.to_text() == ""
    assert result.stop_reason == "refusal"


def test_thinking_blocks(make_message: Callable[..., Message]) -> None:
    result = from_anthropic_message(
        make_message(
            [
                {"type": "thinking", "thinking": "Hmm", "signature": "sig"},
                {"type": "redacted_thinking", "data": "xyz"},
                {"type": "text", "text": "Hi"},
            ]
        ),
        cache_ttl="5m",
    )

    assert result.thinking_blocks == [
        {"type": "thinking", "thinking": "Hmm", "signature": "sig"},
        {"type": "redacted_thinking", "data": "xyz"},
    ]
    assert result.ai_message.to_text() == "Hi"
