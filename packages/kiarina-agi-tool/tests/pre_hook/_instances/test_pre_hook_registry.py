from collections.abc import Iterator

import pytest

from kiarina.agi.pre_hook import BasePreHook, pre_hook_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    pre_hook_registry.clear()


def test_pre_hook_registry() -> None:

    class ExamplePreHook(BasePreHook):
        pass

    pre_hook_registry.register("test", ExamplePreHook)

    instance = pre_hook_registry.create("test")
    assert isinstance(instance, ExamplePreHook)
    assert instance.name == "test"
