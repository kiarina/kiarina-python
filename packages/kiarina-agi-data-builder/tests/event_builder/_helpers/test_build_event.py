import pytest

from kiarina.agi.event import (
    AIMessageEvent,
    CustomEvent,
    HumanMessageEvent,
    ToolMessageEvent,
)
from kiarina.agi.event_builder import build_event
from kiarina.agi.run_context import RunContext


@pytest.fixture
def args(run_context: RunContext) -> dict[str, RunContext]:
    return {"run_context": run_context}


async def test_event(args: dict[str, RunContext]) -> None:
    event = HumanMessageEvent.create("Hello")
    assert await build_event(event, **args) is event


async def test_tuple_custom(args: dict[str, RunContext]) -> None:
    event = await build_event(("custom", {"key": "value"}), **args)
    assert isinstance(event, CustomEvent)
    assert event.payload == {"key": "value"}
    print(event.model_dump_json(indent=2))


async def test_human_message(text_file_path: str, args: dict[str, RunContext]) -> None:
    event = await build_event({"text": "Hello", "files": [text_file_path]}, **args)
    assert isinstance(event, HumanMessageEvent)
    assert "Hello" in event.to_text()
    print(event.model_dump_json(indent=2))


async def test_ai_message(args: dict[str, RunContext]) -> None:
    event = await build_event(
        (
            "ai",
            {
                "text": "Hello",
                "tool_calls": [
                    {
                        "id": "123",
                        "name": "tool1",
                    }
                ],
            },
        ),
        **args,
    )

    assert isinstance(event, AIMessageEvent)
    assert "Hello" in event.to_text()
    assert "tool1" in event.to_text()
    assert len(event.message.tool_calls) == 1
    print(event.model_dump_json(indent=2))


async def test_tool_message(args: dict[str, RunContext]) -> None:
    event = await build_event(
        (
            "tool",
            {
                "text": "Hello",
                "tool_call_id": "123",
                "tool_name": "tool1",
            },
        ),
        **args,
    )

    assert isinstance(event, ToolMessageEvent)
    assert "Hello" in event.to_text()
    assert event.message.tool_name == "tool1"
    print(event.model_dump_json(indent=2))
