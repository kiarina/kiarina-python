from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from kiarina.agi.clock import Clock, SystemClock, get_clock, set_clock


class FixedClock:
    def __init__(self, at: datetime) -> None:
        self.at = at

    def now(self) -> datetime:
        return self.at


@pytest.fixture(autouse=True)
def reset_clock() -> Iterator[None]:
    set_clock(None)
    yield
    set_clock(None)


def test_get_clock_returns_the_system_clock_by_default() -> None:
    clock = get_clock()

    assert isinstance(clock, SystemClock)
    assert get_clock() is clock
    assert clock.now().tzinfo is UTC


def test_set_clock_replaces_the_clock() -> None:
    at = datetime(2026, 1, 1, tzinfo=UTC)
    fixed = FixedClock(at)

    set_clock(fixed)

    assert isinstance(fixed, Clock)
    assert get_clock() is fixed
    assert get_clock().now() == at


def test_set_clock_none_goes_back_to_the_system_clock() -> None:
    set_clock(FixedClock(datetime(2026, 1, 1, tzinfo=UTC)))

    set_clock(None)

    assert isinstance(get_clock(), SystemClock)
