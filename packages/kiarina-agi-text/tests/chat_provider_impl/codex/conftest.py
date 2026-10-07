from collections.abc import Iterator

import pytest

from kiarina.agi.chat_provider_impl.codex._instances.live_thread_pool import (
    live_thread_pool,
)


@pytest.fixture(autouse=True)
def clear_live_threads() -> Iterator[None]:
    yield
    live_thread_pool.clear()
