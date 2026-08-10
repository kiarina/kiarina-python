import pytest

from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from kiarina.agi.message_builder import build_message
from kiarina.agi.run_context import RunContext


@pytest.fixture
def args(run_context: RunContext) -> dict[str, RunContext]:
    return {"run_context": run_context}


async def test_message(args: dict[str, RunContext]) -> None:
    human_message = HumanMessage.create("Hello")
    assert await build_message(human_message, **args) is human_message

    ai_message = AIMessage.create("Hello")
    assert await build_message(ai_message, **args) is ai_message

    tool_message = ToolMessage.create(
        "Hello", tool_name="test_tool", tool_call_id="123"
    )
    assert await build_message(tool_message, **args) is tool_message


async def test_str(args: dict[str, RunContext]) -> None:
    message = await build_message("Hello", **args)
    assert isinstance(message, HumanMessage)
    assert message.to_text() == "Hello"
    print(message.model_dump_json(indent=2))


async def test_spec(text_file_path: str, args: dict[str, RunContext]) -> None:
    message = await build_message({"text": "Hello", "files": [text_file_path]}, **args)
    assert isinstance(message, HumanMessage)
    assert "Hello" in message.to_text()
    assert text_file_path in message.to_text()
    print(message.model_dump_json(indent=2))


async def test_tuple_human_str(args: dict[str, RunContext]) -> None:
    message = await build_message(("human", "Hello"), **args)
    assert isinstance(message, HumanMessage)
    assert message.to_text() == "Hello"
    print(message.model_dump_json(indent=2))


async def test_tuple_human_spec(args: dict[str, RunContext]) -> None:
    message = await build_message(("human", {"text": "Hello"}), **args)
    assert isinstance(message, HumanMessage)
    assert message.to_text() == "Hello"
    print(message.model_dump_json(indent=2))


async def test_tuple_ai_spec(args: dict[str, RunContext]) -> None:
    message = await build_message(
        (
            "ai",
            {
                "text": "Hello",
                "tool_calls": [{"id": "123", "name": "test_tool"}],
            },
        ),
        **args,
    )

    assert isinstance(message, AIMessage)
    assert "Hello" in message.to_text()
    assert "test_tool" in message.to_text()
    print(message.model_dump_json(indent=2))


async def test_tuple_tool_spec(args: dict[str, RunContext]) -> None:
    message = await build_message(
        (
            "tool",
            {
                "text": "Hello",
                "tool_call_id": "123",
                "tool_name": "test_tool",
            },
        ),
        **args,
    )

    assert isinstance(message, ToolMessage)
    assert message.to_text() == "Hello"
    print(message.model_dump_json(indent=2))
