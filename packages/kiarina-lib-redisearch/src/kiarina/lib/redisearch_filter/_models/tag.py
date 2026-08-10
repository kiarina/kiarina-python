from typing import ClassVar

from .._decorators.check_operator_misuse import check_operator_misuse
from .._enums.redisearch_filter_operator import RedisearchFilterOperator
from .._utils.escape_token import escape_token
from .base_field_filter import BaseFieldFilter
from .redisearch_filter import RedisearchFilter


class Tag(BaseFieldFilter):
    # --------------------------------------------------
    # Class Variables
    # --------------------------------------------------

    OPERATORS: ClassVar[dict[RedisearchFilterOperator, str]] = {
        RedisearchFilterOperator.EQ: "==",
        RedisearchFilterOperator.NE: "!=",
        RedisearchFilterOperator.IN: "==",
    }

    OPERATOR_MAP: ClassVar[dict[RedisearchFilterOperator, str]] = {
        RedisearchFilterOperator.EQ: "@%s:{%s}",
        RedisearchFilterOperator.NE: "(-@%s:{%s})",
        RedisearchFilterOperator.IN: "@%s:{%s}",
    }

    SUPPORTED_VALUE_TYPES = (list, set, tuple, str, type(None))

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def _formatted_tag_value(self) -> str:
        return "|".join([escape_token(tag) for tag in self._value])

    # --------------------------------------------------
    # Magic Methods
    # --------------------------------------------------

    def __str__(self) -> str:
        if not self._value:
            return "*"

        return self.OPERATOR_MAP[self._operator] % (
            self._field_name,
            self._formatted_tag_value,
        )

    @check_operator_misuse
    def __eq__(
        self, other: list[str] | set[str] | tuple[str] | str
    ) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.EQ,
            value=self._normalize_tag_value(other),
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    @check_operator_misuse
    def __ne__(
        self, other: list[str] | set[str] | tuple[str] | str
    ) -> RedisearchFilter:
        self._set(
            operator=RedisearchFilterOperator.NE,
            value=self._normalize_tag_value(other),
            value_type=self.SUPPORTED_VALUE_TYPES,  # type: ignore
        )

        return RedisearchFilter(str(self))

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _normalize_tag_value(
        self, other: list[str] | set[str] | tuple[str] | str
    ) -> list[str]:
        if isinstance(other, (list, set, tuple)):
            try:
                return [str(val) for val in other if val]
            except ValueError as e:
                raise ValueError("All tags within collection must be strings") from e

        elif not other:
            return []

        elif isinstance(other, str):
            return [other]

        return []
