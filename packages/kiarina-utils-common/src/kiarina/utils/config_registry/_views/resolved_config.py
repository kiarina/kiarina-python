from typing import Generic, NamedTuple, TypeVar

from .._types.config_name import ConfigName

T = TypeVar("T")


class ResolvedConfig(NamedTuple, Generic[T]):
    name: ConfigName
    config: T
