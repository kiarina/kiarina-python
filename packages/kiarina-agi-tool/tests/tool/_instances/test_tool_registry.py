from collections.abc import Iterator

import pytest

from kiarina.agi.tool import tool, tool_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    tool_registry.clear()


def test_tool_registry() -> None:

    @tool
    def ExampleTool() -> str:
        return "Hello"

    tool_registry.register("test", ExampleTool)

    instance = tool_registry.create("test")
    assert isinstance(instance, ExampleTool)
    assert instance.name == "test"
