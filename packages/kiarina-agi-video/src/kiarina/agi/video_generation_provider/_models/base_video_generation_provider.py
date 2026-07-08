from abc import ABC, abstractmethod

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.video_generation_result import VideoGenerationResult
from .._types.video_generation_provider import VideoGenerationProvider
from .._types.video_generation_provider_name import VideoGenerationProviderName
from .._types.video_generation_session_id import VideoGenerationSessionID


class BaseVideoGenerationProvider(VideoGenerationProvider, ABC):
    def __init__(self) -> None:
        self._name: VideoGenerationProviderName | None = None

    @property
    def name(self) -> VideoGenerationProviderName:
        if self._name is None:
            raise ValueError("VideoGenerationProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: VideoGenerationProviderName) -> None:
        self._name = value

    def __str__(self) -> str:
        return self.__class__.__name__

    async def create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(
            video_generation_provider=f"{self} create",
        )

        return await self._create(
            prompt,
            first_image_file_path=first_image_file_path,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    async def edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(
            video_generation_provider=f"{self} edit",
        )

        return await self._edit(
            prompt,
            session_id=session_id,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    async def extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(
            video_generation_provider=f"{self} extend",
        )

        return await self._extend(
            prompt,
            session_id=session_id,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    @abstractmethod
    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool: ...

    @abstractmethod
    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult: ...

    @abstractmethod
    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None: ...

    @abstractmethod
    async def _create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID: ...

    @abstractmethod
    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID: ...

    @abstractmethod
    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID: ...
