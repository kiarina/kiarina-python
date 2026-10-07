from kiarina.agi.chat_provider_impl.codex_app_server._operations.from_raw_response_items import (
    from_raw_response_items,
)


def test_from_raw_response_items() -> None:
    result = from_raw_response_items(
        [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Hello"}],
            },
            {"type": "reasoning", "summary": []},
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Checking."}],
            },
            {
                "type": "function_call",
                "call_id": "call_1",
                "name": "get_weather",
                "arguments": '{"city": "Nagoya"}',
            },
            {"type": "function_call", "call_id": "call_2", "name": "noop"},
        ],
        {"inputTokens": 10},
    )

    assert result.ai_message.to_text().startswith("Checking.")
    assert [(tc.id, tc.name, tc.args) for tc in result.ai_message.tool_calls] == [
        ("call_1", "get_weather", {"city": "Nagoya"}),
        ("call_2", "noop", {}),
    ]
    assert result.usage == {"inputTokens": 10}


def test_from_raw_response_items_without_usage() -> None:
    result = from_raw_response_items([], None)

    assert result.ai_message.to_text() == ""
    assert result.usage == {}
