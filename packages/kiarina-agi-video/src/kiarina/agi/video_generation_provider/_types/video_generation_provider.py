from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._schemas.video_generation_result import VideoGenerationResult
from .video_generation_provider_name import VideoGenerationProviderName
from .video_generation_session_id import VideoGenerationSessionID


@runtime_checkable
class VideoGenerationProvider(Protocol):
    name: VideoGenerationProviderName

    async def create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID: ...

    async def edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID: ...

    async def extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID: ...

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool: ...

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult: ...

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None: ...
