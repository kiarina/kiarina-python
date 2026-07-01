from typing import Self

from .._enums.redisearch_filter_operator import RedisearchFilterOperator


class RedisearchFilter:
    def __init__(
        self,
        query: str | None = None,
        *,
        left: Self | None = None,
        operator: RedisearchFilterOperator | None = None,
        right: Self | None = None,
    ):
        self._query: str | None = query

        self._left: Self | None = left

        self._operator: RedisearchFilterOperator | None = operator

        self._right: Self | None = right

    def __and__(self, other: Self) -> Self:
        return type(self)(
            left=self,
            operator=RedisearchFilterOperator.AND,
            right=other,
        )

    def __or__(self, other: Self) -> Self:
        return type(self)(
            left=self,
            operator=RedisearchFilterOperator.OR,
            right=other,
        )

    def __str__(self) -> str:
        if self._query:
            return self._query

        if self._left and self._operator and self._right:
            operator = " | " if self._operator == RedisearchFilterOperator.OR else " "

            left, right = str(self._left), str(self._right)

            if (left == right) and (right == "*"):
                return "*"

            if (left == "*") and (right != "*"):
                return right

            if (left != "*") and (right == "*"):
                return left

            return f"({left}{operator}{right})"

        raise ValueError("Improperly initialized RedisearchFilter")
