from collections.abc import Callable

import pytest
from openai.types.responses import Response

from kiarina.agi.chat_provider_impl.openai._exceptions.openai_response_error import (
    OpenAIResponseError,
)
from kiarina.agi.chat_provider_impl.openai._operations.from_response import (
    from_response,
)


def test_from_response(make_response: Callable[..., Response]) -> None:
    result = from_response(
        make_response(
            [
                {"type": "reasoning", "id": "rs_1", "summary": []},
                {
                    "type": "message",
                    "id": "msg_1",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {"type": "output_text", "text": "Hi", "annotations": []},
                        {"type": "refusal", "refusal": " but no."},
                    ],
                },
                {
                    "type": "function_call",
                    "call_id": "call_1",
                    "name": "f",
                    "arguments": '{"a": 1}',
                },
            ],
            usage={
                "input_tokens": 10,
                "input_tokens_details": {"cached_tokens": 2, "cache_write_tokens": 1},
                "output_tokens": 5,
                "output_tokens_details": {"reasoning_tokens": 0},
                "total_tokens": 15,
            },
        )
    )

    assert result.ai_message.contents[0].text == "Hi but no."
    assert result.ai_message.tool_calls[0].id == "call_1"
    assert result.stop_reason == "stop"
    assert result.usage is not None
    assert result.usage.cache_write_tokens == 1


@pytest.mark.parametrize(
    ("reason", "expected"),
    [
        ("max_output_tokens", "max_tokens"),
        ("content_filter", "content_filter"),
        ("max_messages", "stop"),
    ],
)
def test_incomplete(
    make_response: Callable[..., Response], reason: str, expected: str
) -> None:
    result = from_response(
        make_response(status="incomplete", incomplete_details={"reason": reason})
    )

    assert result.stop_reason == expected
    assert result.usage is None


def test_failed(make_response: Callable[..., Response]) -> None:
    with pytest.raises(OpenAIResponseError, match="server_error: boom"):
        from_response(
            make_response(
                status="failed", error={"code": "server_error", "message": "boom"}
            )
        )
