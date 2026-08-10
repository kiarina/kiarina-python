from kiarina.agi.history_builder import build_history
from kiarina.agi.run_context import RunContext


async def test_build_history(text_file_path: str, run_context: RunContext) -> None:
    history = await build_history(
        {
            "events": "Hello",
            "file_infos": [text_file_path],
            "tool_infos": ["hello"],
        },
        run_context=run_context,
    )

    assert len(history.events) == 1
    assert len(history.file_infos) == 1
    assert len(history.tool_infos) == 1
