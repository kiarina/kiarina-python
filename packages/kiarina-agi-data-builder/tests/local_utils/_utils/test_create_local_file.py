from kiarina.agi.local_utils import create_local_file
from kiarina.agi.run_context import RunContext
from kiarina.utils.mime import MIMEBlob


async def test_create_local_file(run_context: RunContext) -> None:
    file = await create_local_file(
        "test.txt",
        MIMEBlob("text/plain", b"Hello, World!"),
        run_context=run_context,
    )

    assert file.text_file_info.raw_text == "Hello, World!"

    file = await create_local_file(
        "test2.txt",
        mime_type="text/plain",
        raw_data=b"Hello, World! Again!",
        run_context=run_context,
    )

    assert file.text_file_info.raw_text == "Hello, World! Again!"
