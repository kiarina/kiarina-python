import numpy as np
import pytest

from kiarina.agi.ocr_model import OCRModel, ocr_image
from kiarina.agi.ocr_model._instances.ocr_model_registry import ocr_model_registry
from kiarina.agi.ocr_model._types.ocr_model_specifier import OCRModelSpecifier
from kiarina.agi.run_context import RunContext


async def test_ocr_image_with_mock(run_context: RunContext) -> None:
    results = await ocr_image(
        np.zeros((10, 12, 3), dtype=np.uint8),
        ocr_options={"ocr_model": "mock"},
        run_context=run_context,
    )
    assert [result.text for result in results] == ["Hello, world!"]


async def test_ocr_image_uses_registry_default(
    run_context: RunContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, OCRModelSpecifier | OCRModel | None] = {}
    real_resolve = ocr_model_registry.resolve

    def fake_resolve(
        object_input: OCRModelSpecifier | OCRModel | None = None,
    ) -> OCRModel:
        captured["input"] = object_input
        return real_resolve("mock")

    monkeypatch.setattr(ocr_model_registry, "resolve", fake_resolve)
    await ocr_image(np.zeros((10, 12, 3), dtype=np.uint8), run_context=run_context)
    assert captured["input"] is None
