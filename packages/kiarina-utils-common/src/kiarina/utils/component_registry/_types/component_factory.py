from typing import Callable, TypeAlias, TypeVar

T = TypeVar("T")

ComponentFactory: TypeAlias = Callable[..., T]
