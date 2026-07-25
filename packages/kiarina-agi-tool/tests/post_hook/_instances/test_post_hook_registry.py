from collections.abc import Iterator

import pytest

from kiarina.agi.post_hook import BasePostHook, post_hook_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    post_hook_registry.clear()


def test_post_hook_registry() -> None:

    class ExamplePostHook(BasePostHook):
        pass

    post_hook_registry.register("test", ExamplePostHook)

    instance = post_hook_registry.create("test")
    assert isinstance(instance, ExamplePostHook)
    assert instance.name == "test"
