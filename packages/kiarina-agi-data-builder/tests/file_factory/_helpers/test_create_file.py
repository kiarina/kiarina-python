from kiarina.agi.file_factory import create_file
from kiarina.agi.run_context import RunContext


async def test_create_file(run_context: RunContext) -> None:
    file = await create_file(
        "test.txt",
        mime_type="text/plain",
        raw_text="Hello, World!",
        run_context=run_context,
    )

    assert file.text_file_info.raw_text == "Hello, World!"

    file = await create_file(
        "test2.txt",
        mime_type="text/plain",
        raw_text="Hello, World!",
        storage="asset",
        run_context=run_context,
    )

    assert file.text_file_info.raw_text == "Hello, World!"
