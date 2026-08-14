import json
from typing import Self

from pydantic import BaseModel, Field, model_validator

type QueryValue = str | bool | int | float


class RTDBQuery(BaseModel):
    """Query parameters for the Firebase Realtime Database REST API."""

    order_by: str | None = Field(
        default=None,
        title="Order by",
        description='Child key to order by, or "$key", "$value" or "$priority".',
    )
    limit_to_first: int | None = Field(
        default=None,
        title="Limit to first",
        description="Number of items to take from the beginning of the ordered result.",
    )
    limit_to_last: int | None = Field(
        default=None,
        title="Limit to last",
        description="Number of items to take from the end of the ordered result.",
    )
    start_at: QueryValue | None = Field(
        default=None,
        title="Start at",
        description="Inclusive lower bound of the ordered result.",
    )
    start_after: QueryValue | None = Field(
        default=None,
        title="Start after",
        description="Exclusive lower bound of the ordered result.",
    )
    end_at: QueryValue | None = Field(
        default=None,
        title="End at",
        description="Inclusive upper bound of the ordered result.",
    )
    end_before: QueryValue | None = Field(
        default=None,
        title="End before",
        description="Exclusive upper bound of the ordered result.",
    )
    equal_to: QueryValue | None = Field(
        default=None,
        title="Equal to",
        description="Exact value the ordered child must match.",
    )
    shallow: bool = Field(
        default=False,
        title="Shallow",
        description="Truncate each value to true. Cannot be combined with other parameters.",
    )

    @model_validator(mode="after")
    def validate_combination(self) -> Self:
        filters = {
            "limit_to_first": self.limit_to_first,
            "limit_to_last": self.limit_to_last,
            "start_at": self.start_at,
            "start_after": self.start_after,
            "end_at": self.end_at,
            "end_before": self.end_before,
            "equal_to": self.equal_to,
        }
        used = [name for name, value in filters.items() if value is not None]

        if self.shallow and (used or self.order_by is not None):
            raise ValueError("shallow cannot be combined with other query parameters")

        if used and self.order_by is None:
            raise ValueError(f"order_by is required when using {', '.join(used)}")

        for left, right in (
            ("limit_to_first", "limit_to_last"),
            ("start_at", "start_after"),
            ("end_at", "end_before"),
        ):
            if filters[left] is not None and filters[right] is not None:
                raise ValueError(f"{left} and {right} are mutually exclusive")

        if self.equal_to is not None and len(used) > 1:
            raise ValueError(
                "equal_to cannot be combined with range or limit parameters"
            )

        return self

    def to_params(self) -> dict[str, str]:
        if self.shallow:
            return {"shallow": "true"}

        params: dict[str, str] = {}

        if self.order_by is not None:
            params["orderBy"] = json.dumps(self.order_by)

        for name, limit in (
            ("limitToFirst", self.limit_to_first),
            ("limitToLast", self.limit_to_last),
        ):
            if limit is not None:
                params[name] = str(limit)

        for name, bound in (
            ("startAt", self.start_at),
            ("startAfter", self.start_after),
            ("endAt", self.end_at),
            ("endBefore", self.end_before),
            ("equalTo", self.equal_to),
        ):
            if bound is not None:
                params[name] = json.dumps(bound)

        return params
