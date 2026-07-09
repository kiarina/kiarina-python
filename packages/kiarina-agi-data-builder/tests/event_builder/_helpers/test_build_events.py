from kiarina.agi.event_builder import build_events
from kiarina.agi.run_context import RunContext


async def test_list(run_context: RunContext, text_file_path: str) -> None:
    events = await build_events(
        [
            ("human", {"text": "Hello", "files": [text_file_path]}),
            ("ai", "Hello"),
            ("human", "Use tool1"),
            (
                "ai",
                {
                    "text": "OK",
                    "tool_calls": [
                        {
                            "id": "123",
                            "name": "tool1",
                        }
                    ],
                },
            ),
            (
                "tool",
                {
                    "text": "tool1 called",
                    "files": [text_file_path],
                    "tool_call_id": "123",
                    "tool_name": "tool1",
                },
            ),
            ("custom", {"key": "value"}),
        ],
        run_context=run_context,
    )

    assert len(events) == 6

    for i, event in enumerate(events):
        print(f"--- [{i}] {event.type} ---")
        print(event.model_dump_json(indent=2))


async def test_not_list(run_context: RunContext, text_file_path: str) -> None:
    events = await build_events(
        {"text": "Hello", "files": [text_file_path]}, run_context=run_context
    )

    assert len(events) == 1

    for event in events:
        print(f"--- {event.type} ---")
        print(event.model_dump_json(indent=2))
