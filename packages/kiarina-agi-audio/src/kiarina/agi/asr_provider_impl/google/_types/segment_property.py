from typing import Literal, NotRequired, TypedDict


class SegmentProperty(TypedDict):
    type: Literal["string", "number", "boolean"]
    description: NotRequired[str]
    enum: NotRequired[list[str]]
