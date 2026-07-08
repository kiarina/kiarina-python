import logging
import uuid

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider import (
    BaseVideoGenerationProvider,
    VideoGenerationResult,
    VideoGenerationSessionID,
)
from kiarina.utils.file.asyncio import read_file

from .._services.session_store import SessionStore
from .._settings import MockVideoGenerationProviderSettings

logger = logging.getLogger(__name__)


class MockVideoGenerationProvider(BaseVideoGenerationProvider):
    """
    Mock Video Provider Implementation for Testing
    """

    def __init__(self, settings: MockVideoGenerationProviderSettings) -> None:
        super().__init__()

        self.settings: MockVideoGenerationProviderSettings = settings
        self._store = SessionStore.get_instance()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"

    # --------------------------------------------------
    # Private Methods (Video Generation)
    # --------------------------------------------------

    async def _create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        session_id = f"mock_video_{uuid.uuid4().hex[:16]}"

        logger.info(f"Mock video create: {prompt} (session: {session_id})")

        await self._store.create(
            session_id,
            prompt,
            delay_seconds=self.settings.delay_seconds,
        )

        return session_id

    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        new_session_id = f"mock_video_{uuid.uuid4().hex[:16]}"

        logger.info(
            f"Mock video edit: {prompt} (old: {session_id}, new: {new_session_id})"
        )

        await self._store.create(
            new_session_id,
            prompt,
            delay_seconds=self.settings.delay_seconds,
        )

        return new_session_id

    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        new_session_id = f"mock_video_{uuid.uuid4().hex[:16]}"

        logger.info(
            f"Mock video extend: {prompt} (old: {session_id}, new: {new_session_id})"
        )

        await self._store.create(
            new_session_id,
            prompt,
            delay_seconds=self.settings.delay_seconds,
        )

        return new_session_id

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool:
        session = await self._store.get(session_id)

        if not session:
            return False

        return not await self._store.is_completed(session_id)

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult:
        session = await self._store.get(session_id)

        if not session:
            raise ValueError(f"Session {session_id} not found")

        if not await self._store.is_completed(session_id):
            raise RuntimeError(
                f"Mock video session {session_id} is still running. "
                "Please wait until it completes before calling get()."
            )

        if not self.settings.result_video_file_path:
            raise RuntimeError(
                "No result video file path configured in settings "
                "('result_video_file_path')."
            )

        video_file_blob = await read_file(self.settings.result_video_file_path)

        if not video_file_blob:
            raise RuntimeError(
                f"Failed to read video file from "
                f"'{self.settings.result_video_file_path}'."
            )

        return VideoGenerationResult(
            video_mime_blob=video_file_blob.mime_blob,
        )

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None:
        await self._store.delete(session_id)
        logger.info(f"Deleted mock video session: {session_id}")
