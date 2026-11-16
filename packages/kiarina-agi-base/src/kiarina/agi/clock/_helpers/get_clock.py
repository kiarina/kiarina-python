from .._instances import current_clock as holder
from .._services.system_clock import SystemClock
from .._types.clock import Clock


def get_clock() -> Clock:
    if holder.current_clock is None:
        holder.current_clock = SystemClock()
    return holder.current_clock
