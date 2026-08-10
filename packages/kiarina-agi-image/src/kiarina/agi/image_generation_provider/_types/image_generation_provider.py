from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._views.image_generation_result import ImageGenerationResult
from .image_generation_provider_name import ImageGenerationProviderName


@runtime_checkable
class ImageGenerationProvider(Protocol):
    name: ImageGenerationProviderName

    async def generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageGenerationResult: ...
