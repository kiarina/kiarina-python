from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider import (
    BaseVideoGenerationProvider,
    VideoGenerationResult,
    VideoGenerationSessionID,
)
from kiarina.utils.mime import MIMEBlob


class VideoGenerationProvider(BaseVideoGenerationProvider):
    def __init__(self, *args: Any) -> None: ...

    async def _create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        cost_recorder.add(self._cost_record())
        return "session_create"

    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        cost_recorder.add(self._cost_record())
        return "session_edit"

    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        cost_recorder.add(self._cost_record())
        return "session_extend"

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool:
        return False

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult:
        return VideoGenerationResult(
            video_mime_blob=MIMEBlob(mime_type="video/mp4", raw_text="test_video"),
        )

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None:
        pass

    def _cost_record(self) -> CostRecord:
        return CostRecord(
            microdollars=1,
            kind="video",
            source="test_provider",
        )


async def test_base_video_generation_provider_create(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = VideoGenerationProvider()

    session_id = await provider.create(
        prompt="A cute cat playing",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_create"
    assert cost_recorder.total_microdollars == 1


async def test_base_video_generation_provider_create_with_first_image(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = VideoGenerationProvider()

    session_id = await provider.create(
        prompt="A cute cat playing",
        first_image_file_path="/path/to/image.jpg",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_create"
    assert cost_recorder.total_microdollars == 1


async def test_base_video_generation_provider_edit(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = VideoGenerationProvider()

    session_id = await provider.edit(
        prompt="Add a hat to the cat",
        session_id="session_123",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_edit"
    assert cost_recorder.total_microdollars == 1


async def test_base_video_generation_provider_extend(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = VideoGenerationProvider()

    session_id = await provider.extend(
        prompt="Continue the video",
        session_id="session_123",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_extend"
    assert cost_recorder.total_microdollars == 1


async def test_base_video_generation_provider_is_running(
    run_context: RunContext,
) -> None:
    provider = VideoGenerationProvider()

    is_running = await provider.is_running(
        session_id="session_123",
        run_context=run_context,
    )

    assert is_running is False


async def test_base_video_generation_provider_get(run_context: RunContext) -> None:
    provider = VideoGenerationProvider()

    result = await provider.get(
        session_id="session_123",
        run_context=run_context,
    )

    assert result.video_mime_blob.mime_type == "video/mp4"
    assert result.video_mime_blob.raw_text == "test_video"


async def test_base_video_generation_provider_delete(run_context: RunContext) -> None:
    provider = VideoGenerationProvider()

    # Should not raise any exception
    await provider.delete(
        session_id="session_123",
        run_context=run_context,
    )
