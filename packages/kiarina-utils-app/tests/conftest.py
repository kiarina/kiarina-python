from collections.abc import Iterator

import pytest

from kiarina.utils.app._instances.app import app
from kiarina.utils.app._services import single_instance


@pytest.fixture(autouse=True)
def reset_state() -> Iterator[None]:
    yield
    single_instance.release()
    app.reset()
