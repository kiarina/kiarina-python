from collections.abc import Callable
from typing import Any

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.responses import Response


@pytest.fixture
def make_response() -> Callable[..., Response]:
    def factory(
        output: list[dict[str, Any]] | None = None, **overrides: Any
    ) -> Response:
        return Response.model_validate(
            {
                "id": "resp_1",
                "created_at": 0,
                "model": "gpt-test",
                "object": "response",
                "output": output or [],
                "parallel_tool_calls": False,
                "tool_choice": "auto",
                "tools": [],
                "status": "completed",
                **overrides,
            }
        )

    return factory


@pytest.fixture
def make_completion() -> Callable[..., ChatCompletion]:
    def factory(
        message: dict[str, Any] | None = None,
        finish_reason: str = "stop",
        **overrides: Any,
    ) -> ChatCompletion:
        return ChatCompletion.model_validate(
            {
                "id": "chatcmpl_1",
                "created": 0,
                "model": "gpt-test",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": finish_reason,
                        "message": {"role": "assistant", **(message or {})},
                    }
                ],
                **overrides,
            }
        )

    return factory


@pytest.fixture
def make_chunk() -> Callable[..., ChatCompletionChunk]:
    def factory(
        delta: dict[str, Any] | None = None,
        finish_reason: str | None = None,
        **overrides: Any,
    ) -> ChatCompletionChunk:
        choices = (
            [{"index": 0, "delta": delta or {}, "finish_reason": finish_reason}]
            if delta is not None or finish_reason
            else []
        )

        return ChatCompletionChunk.model_validate(
            {
                "id": "chatcmpl_1",
                "created": 0,
                "model": "gpt-test",
                "object": "chat.completion.chunk",
                "choices": choices,
                **overrides,
            }
        )

    return factory
