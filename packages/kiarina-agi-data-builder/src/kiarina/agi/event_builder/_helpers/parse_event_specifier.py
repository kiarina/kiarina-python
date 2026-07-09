import json
from typing import cast

from .._types.event_input import EventInput
from .._types.event_specifier import EventSpecifier


def parse_event_specifier(specifier: EventSpecifier) -> EventInput:
    if not specifier.startswith("{") and not specifier.startswith("["):
        return specifier

    try:
        data = json.loads(specifier)
    except json.JSONDecodeError:  # pragma: no cover
        return specifier

    if isinstance(data, list):
        return cast(EventInput, tuple(data))

    return cast(EventInput, data)
