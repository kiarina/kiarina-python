from collections.abc import Iterator

import pytest

from kiarina.agi.tool_logger import BaseToolLogger, tool_logger_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    tool_logger_registry.clear()


def test_tool_logger_registry() -> None:

    class ExampleToolLogger(BaseToolLogger):
        pass

    tool_logger_registry.register("test", ExampleToolLogger)

    instance = tool_logger_registry.create("test")
    assert isinstance(instance, ExampleToolLogger)
    assert instance.name == "test"
