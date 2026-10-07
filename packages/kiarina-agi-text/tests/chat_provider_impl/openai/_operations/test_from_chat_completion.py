from collections.abc import Callable

from openai.types.chat import ChatCompletion

from kiarina.agi.chat_provider_impl.openai._operations.from_chat_completion import (
    from_chat_completion,
)


def test_from_chat_completion(make_completion: Callable[..., ChatCompletion]) -> None:
    result = from_chat_completion(
        make_completion(
            {
                "content": "Hi",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "f", "arguments": '{"a": 1}'},
                    }
                ],
            },
            finish_reason="tool_calls",
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "prompt_tokens_details": {"cached_tokens": 4},
            },
        )
    )

    assert result.ai_message.to_text().startswith("Hi")
    assert result.ai_message.tool_calls[0].id == "call_1"
    assert result.ai_message.tool_calls[0].args == {"a": 1}
    assert result.stop_reason == "stop"
    assert result.usage is not None
    assert result.usage.cached_input_tokens == 4


def test_refusal(make_completion: Callable[..., ChatCompletion]) -> None:
    result = from_chat_completion(
        make_completion({"refusal": "No."}, finish_reason="content_filter")
    )

    assert result.ai_message.to_text() == "No."
    assert result.stop_reason == "content_filter"
    assert result.usage is None
