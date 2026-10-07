from collections.abc import Callable

from google.genai import types

from kiarina.agi.chat_provider_impl.google_genai._operations.from_google_genai_response import (
    from_google_genai_response,
)


def test_from_google_genai_response(
    make_response: Callable[..., types.GenerateContentResponse],
) -> None:
    result = from_google_genai_response(
        make_response(
            [
                {"text": "Thinking...", "thought": True},
                {"text": "Hi"},
                {"function_call": {"id": "call_1", "name": "f", "args": {"a": 1}}},
                {"function_call": {"name": "g", "args": {}}},
            ],
            usage={"prompt_token_count": 10, "candidates_token_count": 5},
        ),
        tool_call_ids={1: "from-stream"},
    )

    assert result.ai_message.contents[0].text == "Hi"
    assert [(tc.id, tc.name, tc.args) for tc in result.ai_message.tool_calls] == [
        ("call_1", "f", {"a": 1}),
        ("from-stream", "g", {}),
    ]
    assert result.stop_reason == "stop"
    assert result.usage is not None
    assert result.usage.output_tokens == 5


def test_generated_tool_call_id(
    make_response: Callable[..., types.GenerateContentResponse],
) -> None:
    result = from_google_genai_response(
        make_response([{"function_call": {"name": "f"}}])
    )

    assert result.ai_message.tool_calls[0].id


def test_blocked_prompt() -> None:
    result = from_google_genai_response(
        types.GenerateContentResponse.model_validate(
            {"prompt_feedback": {"block_reason": "SAFETY"}}
        )
    )

    assert result.stop_reason == "safety"
    assert result.ai_message.to_text() == ""
