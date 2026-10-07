from collections.abc import Callable
from typing import Any

import pytest
from anthropic.types import Message


@pytest.fixture
def make_message() -> Callable[..., Message]:
    def factory(
        content: list[dict[str, Any]] | None = None,
        stop_reason: str = "end_turn",
        **usage: Any,
    ) -> Message:
        return Message.model_validate(
            {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "model": "claude-test",
                "content": content or [],
                "stop_reason": stop_reason,
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 5, **usage},
            }
        )

    return factory
