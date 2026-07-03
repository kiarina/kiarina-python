from typing import Any, Literal, Self

from pydantic import Field

from .base_event import BaseEvent


class CustomEvent(BaseEvent):
    type: Literal["custom"] = Field(default="custom", frozen=True)
    payload: dict[str, Any] = Field(default_factory=dict)

    def to_text(self) -> str:
        if custom_type := self.payload.get("type"):
            return str(custom_type)
        else:
            return super().to_text()

    @classmethod
    def create(cls, **kwargs: Any) -> Self:
        return cls(payload=kwargs)
