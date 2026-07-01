from typing import Any, ClassVar, Self

from .._enums.redisearch_filter_operator import RedisearchFilterOperator


class BaseFieldFilter:
    OPERATORS: ClassVar[dict[RedisearchFilterOperator, str]] = {}

    def __init__(self, field_name: str):
        self._field_name: str = field_name

        self._operator: RedisearchFilterOperator = RedisearchFilterOperator.EQ

        self._value: Any = None

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def equals(self, other: Self) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self._field_name == other._field_name and self._value == other._value

    # --------------------------------------------------
    # Protected Methods
    # --------------------------------------------------

    def _set(
        self,
        *,
        operator: RedisearchFilterOperator,
        value: Any,
        value_type: tuple[Any],
    ) -> None:
        if operator not in self.OPERATORS:
            raise ValueError(
                f"Operator {operator} not supported by {self.__class__.__name__}. "
                f"Supported operators are {self.OPERATORS.values()}."
            )

        if not isinstance(value, value_type):
            raise TypeError(
                f"Right side argument passed to operator {self.OPERATORS[operator]} "
                f"with left side "
                f"argument {self.__class__.__name__} must be of type {value_type}, "
                f"received value {value}"
            )

        self._operator = operator
        self._value = value
