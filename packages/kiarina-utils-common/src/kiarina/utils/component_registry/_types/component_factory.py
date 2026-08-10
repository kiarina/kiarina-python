from collections.abc import Callable
from typing import TypeAlias, TypeVar

T = TypeVar("T")

ComponentFactory: TypeAlias = Callable[..., T]
