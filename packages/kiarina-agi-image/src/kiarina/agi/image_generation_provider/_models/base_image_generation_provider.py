from abc import ABC, abstractmethod

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.run_context import RunContext

from .._types.image_generation_provider import ImageGenerationProvider
from .._types.image_generation_provider_name import ImageGenerationProviderName
from .._views.image_generation_result import ImageGenerationResult


class BaseImageGenerationProvider(ImageGenerationProvider, ABC):
    def __init__(self) -> None:
        self._name: ImageGenerationProviderName | None = None

    @property
    def name(self) -> ImageGenerationProviderName:
        if self._name is None:
            raise ValueError("ImageGenerationProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: ImageGenerationProviderName) -> None:
        self._name = value

    def __str__(self) -> str:
        return self.__class__.__name__

    async def generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(
            image_generation_provider=str(self),
        )

        return await self._generate(
            prompt,
            file_paths=file_paths,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    @abstractmethod
    async def _generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult: ...
