from typing import ClassVar

from .._decorators.check_operator_misuse import check_operator_misuse
from .._enums.redisearch_filter_operator import RedisearchFilterOperator
from .base_field_filter import BaseFieldFilter
from .redisearch_filter import RedisearchFilter


class Text(BaseFieldFilter):
    # --------------------------------------------------
    # Class Variables
    # --------------------------------------------------

    OPERATORS: ClassVar[dict[RedisearchFilterOperator, str]] = {
        RedisearchFilterOperator.EQ: "==",
        RedisearchFilterOperator.NE: "!=",
        RedisearchFilterOperator.LIKE: "%",
    }

    OPERATOR_MAP: ClassVar[dict[RedisearchFilterOperator, str]] = {
        RedisearchFilterOperator.EQ: '@%s:("%s")',
        RedisearchFilterOperator.NE: '(-@%s:"%s")',
        RedisearchFilterOperator.LIKE: "@%s:(%s)",
    }

    SUPPORTED_VALUE_TYPES = (str, type(None))

    # --------------------------------------------------
    # Magic Methods
    # --------------------------------------------------

    def __str__(self) -> str:
        if not self._value:
            return "*"

        return self.OPERATOR_MAP[self._operator] % (
            self._field_name,
            self._value,
        )

    @check_operator_misuse
    def __eq__(self, other: str) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.EQ,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    @check_operator_misuse
    def __ne__(self, other: str) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.NE,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    def __mod__(self, other: str) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.LIKE,
            value=other,
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))
