from kiarina.agi.file_factory import create_markdown_file
from kiarina.agi.run_context import RunContext


async def test_create_markdown_file(run_context: RunContext) -> None:
    file = await create_markdown_file(
        "test.md",
        content="Hello, World!",
        metadata={"author": "Test"},
        run_context=run_context,
    )

    assert "Hello, World!" in (file.text_file_info.raw_text or "")
    assert "author: Test" in (file.text_file_info.raw_text or "")
