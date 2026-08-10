from typing import ClassVar

from .._decorators.check_operator_misuse import check_operator_misuse
from .._enums.redisearch_filter_operator import RedisearchFilterOperator
from .base_field_filter import BaseFieldFilter
from .redisearch_filter import RedisearchFilter


class Numeric(BaseFieldFilter):
    # --------------------------------------------------
    # Class Variables
    # --------------------------------------------------

    OPERATORS: ClassVar[dict[RedisearchFilterOperator, str]] = {
        RedisearchFilterOperator.EQ: "==",
        RedisearchFilterOperator.NE: "!=",
        RedisearchFilterOperator.LT: "<",
        RedisearchFilterOperator.GT: ">",
        RedisearchFilterOperator.LE: "<=",
        RedisearchFilterOperator.GE: ">=",
    }

    OPERATOR_MAP: ClassVar[dict[RedisearchFilterOperator, str]] = {
        RedisearchFilterOperator.EQ: "@%s:[%s %s]",
        RedisearchFilterOperator.NE: "(-@%s:[%s %s])",
        RedisearchFilterOperator.GT: "@%s:[(%s +inf]",
        RedisearchFilterOperator.LT: "@%s:[-inf (%s]",
        RedisearchFilterOperator.GE: "@%s:[%s +inf]",
        RedisearchFilterOperator.LE: "@%s:[-inf %s]",
    }

    SUPPORTED_VALUE_TYPES = (int, float, type(None))

    # --------------------------------------------------
    # Magic Methods
    # --------------------------------------------------

    def __str__(self) -> str:
        if self._value is None:
            return "*"

        if (
            self._operator == RedisearchFilterOperator.EQ
            or self._operator == RedisearchFilterOperator.NE
        ):
            return self.OPERATOR_MAP[self._operator] % (
                self._field_name,
                self._value,
                self._value,
            )
        else:
            return self.OPERATOR_MAP[self._operator] % (self._field_name, self._value)

    @check_operator_misuse
    def __eq__(self, other: int | float) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.EQ,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    @check_operator_misuse
    def __ne__(self, other: int | float) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.NE,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    def __gt__(self, other: int | float) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.GT,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    def __lt__(self, other: int | float) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.LT,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    def __ge__(self, other: int | float) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.GE,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    def __le__(self, other: int | float) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.LE,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))
