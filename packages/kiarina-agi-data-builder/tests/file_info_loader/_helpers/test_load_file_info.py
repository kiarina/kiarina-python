from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.run_context import RunContext


async def test_file_info(run_context: RunContext) -> None:
    text_file_info = TextFileInfo(
        uri_or_file_path="/path/to/file.txt",
        mime_type="text/plain",
        file_hash="dummy",
        file_size=123,
        intermediate_file_path=None,
        asset_uri=None,
        token_count=10,
        line_count=1,
        raw_text="Hello",
    )

    file_info = await load_file_info(text_file_info, run_context=run_context)
    assert file_info is text_file_info


async def test_file_info_spec(run_context: RunContext, text_file_path: str) -> None:
    file_info = await load_file_info(
        {"uri_or_file_path": text_file_path},
        run_context=run_context,
    )
    assert file_info is not None


async def test_file_info_specifier(
    run_context: RunContext, text_file_path: str
) -> None:
    file_info = await load_file_info(text_file_path, run_context=run_context)
    assert file_info is not None

    file_info = await load_file_info(
        f"{text_file_path}?group=hello",
        run_context=run_context,
    )
    assert file_info is not None
    assert file_info.group == "hello"


async def test_not_found(run_context: RunContext) -> None:
    file_info = await load_file_info("not-found.txt", run_context=run_context)
    assert file_info is None
