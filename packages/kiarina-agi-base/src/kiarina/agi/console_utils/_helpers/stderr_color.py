import sys
from collections.abc import Iterator
from contextlib import contextmanager

from .._types.console_color import ConsoleColor

_COLOR_CODES: dict[ConsoleColor, str] = {
    "black": "\033[90m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
}


@contextmanager
def stderr_color(color: ConsoleColor) -> Iterator[None]:
    if not sys.stderr.isatty():
        yield
        return

    print(_COLOR_CODES[color], end="", flush=True, file=sys.stderr)

    try:
        yield
    finally:
        print("\033[0m", end="", flush=True, file=sys.stderr)
