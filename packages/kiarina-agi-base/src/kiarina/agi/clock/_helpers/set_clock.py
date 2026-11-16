from .._instances import current_clock as holder
from .._types.clock import Clock


def set_clock(clock: Clock | None) -> None:
    holder.current_clock = clock
