from unittest.mock import AsyncMock

import pytest

from kiarina.agi.image_generation_model import (
    ImageGenerationModel,
    ImageGenerationModelConfig,
    generate_image,
)
from kiarina.agi.run_context import RunContext


async def test_generate_image_creates_run_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = ImageGenerationModel(
        "mock",
        ImageGenerationModelConfig(provider_name="mock"),
    )
    result = object()
    generate = AsyncMock(return_value=result)
    monkeypatch.setattr(model, "generate", generate)

    actual = await generate_image(
        "Generate an image",
        image_generation_options={"image_generation_model": model},
    )

    assert actual is result
    assert generate.await_args is not None
    run_context = generate.await_args.kwargs["run_context"]
    assert isinstance(run_context, RunContext)
    assert run_context.metadata["image_generation_model"] == "mock"


async def test_generate_image_extends_explicit_run_context(
    run_context: RunContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    model = ImageGenerationModel(
        "mock",
        ImageGenerationModelConfig(provider_name="mock"),
    )
    result = object()
    generate = AsyncMock(return_value=result)
    monkeypatch.setattr(model, "generate", generate)

    actual = await generate_image(
        "Generate an image",
        image_generation_options={"image_generation_model": model},
        run_context=run_context,
    )

    assert actual is result
    assert generate.await_args is not None
    actual_run_context = generate.await_args.kwargs["run_context"]
    assert actual_run_context.organization_id == run_context.organization_id
    assert actual_run_context.metadata["image_generation_model"] == "mock"
