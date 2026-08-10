from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider import (
    VideoGenerationProvider,
    VideoGenerationProviderName,
    VideoGenerationResult,
    VideoGenerationSessionID,
    video_generation_provider_registry,
)

from .._schemas.video_generation_capabilities import VideoGenerationCapabilities
from .._schemas.video_generation_model_config import VideoGenerationModelConfig
from .._types.video_generation_model_name import VideoGenerationModelName


class VideoGenerationModel:
    def __init__(
        self,
        name: VideoGenerationModelName,
        config: VideoGenerationModelConfig,
    ) -> None:
        self.name: VideoGenerationModelName = name
        self.config: VideoGenerationModelConfig = config
        self._provider: VideoGenerationProvider | None = None

    def __str__(self) -> str:
        return self.name

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def provider_name(self) -> VideoGenerationProviderName:
        return self.config.provider_name

    @property
    def provider_config(self) -> dict[str, Any]:
        return self.config.provider_config

    @property
    def capabilities(self) -> VideoGenerationCapabilities:
        return self.config.capabilities

    @property
    def provider(self) -> VideoGenerationProvider:
        if self._provider is None:
            self._provider = video_generation_provider_registry.create(
                self.provider_name, **self.provider_config
            )

        return self._provider

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    async def create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        return await self.provider.create(
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
        if not self.capabilities.edit_enabled:
            raise NotImplementedError(
                f"Video editing is not supported by model '{self.name}'"
            )

        return await self.provider.edit(
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
        if not self.capabilities.extend_enabled:
            raise NotImplementedError(
                f"Video extension is not supported by model '{self.name}'"
            )

        return await self.provider.extend(
            prompt,
            session_id=session_id,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool:
        return await self.provider.is_running(
            session_id,
            run_context=run_context,
        )

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult:
        return await self.provider.get(
            session_id,
            run_context=run_context,
        )

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None:
        return await self.provider.delete(
            session_id,
            run_context=run_context,
        )
