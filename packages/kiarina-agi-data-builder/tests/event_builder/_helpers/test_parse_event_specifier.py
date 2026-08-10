from kiarina.agi.event_builder import parse_event_specifier


def test_parse_event_specifier() -> None:
    assert parse_event_specifier("Hello") == "Hello"
    assert parse_event_specifier(
        '{"text": "Hello", "files": ["/path/to/file.txt"]}'
    ) == {"text": "Hello", "files": ["/path/to/file.txt"]}
    assert parse_event_specifier('["ai", "Hello"]') == ("ai", "Hello")
    assert parse_event_specifier(
        '["ai", {"text": "Hello", "tool_calls": [{"name": "hello", "args": {"message": "Hello"}}]}]'
    ) == (
        "ai",
        {
            "text": "Hello",
            "tool_calls": [{"name": "hello", "args": {"message": "Hello"}}],
        },
    )
    assert parse_event_specifier(
        '["tool", {"text": "Hello", "tool_call_id": "1234", "tool_name": "hello"}]'
    ) == (
        "tool",
        {
            "text": "Hello",
            "tool_call_id": "1234",
            "tool_name": "hello",
        },
    )
    assert parse_event_specifier('["custom", {"custom_key": "custom_value"}]') == (
        "custom",
        {"custom_key": "custom_value"},
    )
