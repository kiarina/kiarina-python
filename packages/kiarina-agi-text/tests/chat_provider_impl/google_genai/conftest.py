from collections.abc import Callable
from typing import Any

import pytest
from google.genai import types


@pytest.fixture
def make_response() -> Callable[..., types.GenerateContentResponse]:
    def factory(
        parts: list[dict[str, Any]] | None = None,
        finish_reason: str | None = "STOP",
        usage: dict[str, Any] | None = None,
        **overrides: Any,
    ) -> types.GenerateContentResponse:
        return types.GenerateContentResponse.model_validate(
            {
                "candidates": [
                    {
                        "content": {"role": "model", "parts": parts or []},
                        "finish_reason": finish_reason,
                    }
                ],
                "usage_metadata": usage,
                **overrides,
            }
        )

    return factory
