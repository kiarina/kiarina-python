from collections.abc import Iterator

import pytest

from kiarina.agi.request_logger import BaseRequestLogger, request_logger_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    request_logger_registry.clear()


def test_request_logger_registry() -> None:

    class ExampleRequestLogger(BaseRequestLogger):
        pass

    request_logger_registry.register("test", ExampleRequestLogger)

    request_logger = request_logger_registry.create("test")
    assert isinstance(request_logger, ExampleRequestLogger)
    assert request_logger.name == "test"
