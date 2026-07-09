import pytest

from kiarina.agi.content import Content
from kiarina.agi.content_builder import build_content
from kiarina.agi.run_context import RunContext


@pytest.fixture
def args(run_context: RunContext) -> dict[str, RunContext]:
    return {"run_context": run_context}


async def test_content(args: dict[str, RunContext]) -> None:
    content = await build_content(Content(text="Hello"), **args)
    assert content.text == "Hello"
    print(content.model_dump_json(indent=2))


async def test_str(args: dict[str, RunContext]) -> None:
    content = await build_content("Hello", **args)
    assert content.text == "Hello"
    print(content.model_dump_json(indent=2))


async def test_files(text_file_path: str, args: dict[str, RunContext]) -> None:
    content = await build_content({"text": "Hello", "files": [text_file_path]}, **args)
    assert content.text == "Hello"
    assert len(content.files) == 1
    assert content.files[0].uri_or_file_path == text_file_path
    print(content.model_dump_json(indent=2))
