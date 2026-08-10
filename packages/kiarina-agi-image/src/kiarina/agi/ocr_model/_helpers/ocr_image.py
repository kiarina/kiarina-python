from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.ocr_provider import OCRResult
from kiarina.agi.run_context import RunContext

from .._instances.ocr_model_registry import ocr_model_registry
from .._models.ocr_model import OCRModel
from .._types.ocr_options import OCROptions


async def ocr_image(
    pixels: ImagePixels,
    *,
    ocr_options: OCROptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> list[OCRResult]:
    ocr_options = ocr_options or {}
    ocr_model = ocr_options.get("ocr_model")
    if not isinstance(ocr_model, OCRModel):
        ocr_model = ocr_model_registry.resolve(ocr_model)
    run_context = run_context.with_metadata(ocr_model=str(ocr_model))
    return await ocr_model.ocr(
        pixels,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
