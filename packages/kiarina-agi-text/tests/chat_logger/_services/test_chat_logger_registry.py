from collections.abc import Iterator

import pytest

from kiarina.agi.chat_logger import BaseChatLogger, chat_logger_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    chat_logger_registry.clear()


def test_chat_logger_registry() -> None:

    class ExampleChatLogger(BaseChatLogger):
        pass

    chat_logger_registry.register("test", ExampleChatLogger)

    instance = chat_logger_registry.create("test")
    assert isinstance(instance, ExampleChatLogger)
    assert instance.name == "test"
