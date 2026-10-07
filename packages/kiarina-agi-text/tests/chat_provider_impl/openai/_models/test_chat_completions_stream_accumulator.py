from collections.abc import Callable

from openai.types.chat import ChatCompletionChunk

from kiarina.agi.chat_provider_impl.openai._models.chat_completions_stream_accumulator import (
    ChatCompletionsStreamAccumulator,
)


def test_accumulate(make_chunk: Callable[..., ChatCompletionChunk]) -> None:
    accumulator = ChatCompletionsStreamAccumulator()

    def tool_delta(index: int, **function: str) -> dict[str, object]:
        delta: dict[str, object] = {"index": index, "function": function}
        if "name" in function:
            delta["id"] = f"call_{index}"
            delta["type"] = "function"
        return {"tool_calls": [delta]}

    chunks = [
        make_chunk({"role": "assistant", "content": ""}),
        make_chunk({"content": "Hel"}),
        make_chunk({"content": "lo"}),
        make_chunk(tool_delta(1, name="b", arguments="")),
        make_chunk(tool_delta(0, name="a", arguments='{"x"')),
        make_chunk(tool_delta(0, arguments=": 1}")),
        make_chunk(finish_reason="tool_calls"),
        make_chunk(
            usage={"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7}
        ),
    ]

    ai_message_chunks = [c for chunk in chunks if (c := accumulator.add(chunk))]

    assert [c.contents[0].text for c in ai_message_chunks[:2]] == ["Hel", "lo"]
    assert ai_message_chunks[2].tool_call_chunks[0].name == "b"
    assert ai_message_chunks[4].tool_call_chunks[0].args == ": 1}"

    result = accumulator.to_result()

    assert result.ai_message.contents[0].text == "Hello"
    assert [(tc.id, tc.name, tc.args) for tc in result.ai_message.tool_calls] == [
        ("call_0", "a", {"x": 1}),
        ("call_1", "b", {}),
    ]
    assert result.stop_reason == "stop"
    assert result.usage is not None
    assert result.usage.output_tokens == 4


def test_tool_call_without_function(
    make_chunk: Callable[..., ChatCompletionChunk],
) -> None:
    accumulator = ChatCompletionsStreamAccumulator()
    chunk = accumulator.add(make_chunk({"tool_calls": [{"index": 0, "id": "call_0"}]}))

    assert chunk is not None
    assert chunk.tool_call_chunks[0].id == "call_0"
    assert chunk.tool_call_chunks[0].name is None
