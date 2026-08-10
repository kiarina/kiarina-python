from collections.abc import Iterator
from typing import Any

import pytest

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_model import (
    VideoGenerationCapabilities,
    VideoGenerationModel,
    VideoGenerationModelConfig,
)
from kiarina.agi.video_generation_provider import (
    BaseVideoGenerationProvider,
    VideoGenerationResult,
    VideoGenerationSessionID,
    settings_manager,
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
        return "session_123"

    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        cost_recorder.add(self._cost_record())
        return "session_456"

    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        cost_recorder.add(self._cost_record())
        return "session_789"

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
            source="my_video_generation_provider",
        )


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "customs": {"my_provider": __name__ + ":VideoGenerationProvider"}
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def video_generation_model() -> VideoGenerationModel:
    return VideoGenerationModel(
        "my_model",
        VideoGenerationModelConfig(
            provider_name="my_provider",
            capabilities=VideoGenerationCapabilities(
                edit_enabled=True,
                extend_enabled=True,
            ),
        ),
    )


async def test_video_generation_model_create(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    video_generation_model: VideoGenerationModel,
) -> None:
    session_id = await video_generation_model.create(
        "A cute cat playing",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_123"
    assert cost_recorder.total_microdollars == 1


async def test_video_generation_model_edit(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    video_generation_model: VideoGenerationModel,
) -> None:
    session_id = await video_generation_model.edit(
        "Add a hat to the cat",
        session_id="session_123",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_456"
    assert cost_recorder.total_microdollars == 1


async def test_video_generation_model_extend(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    video_generation_model: VideoGenerationModel,
) -> None:
    session_id = await video_generation_model.extend(
        "Continue the video",
        session_id="session_123",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert session_id == "session_789"
    assert cost_recorder.total_microdollars == 1


async def test_video_generation_model_is_running(
    run_context: RunContext, video_generation_model: VideoGenerationModel
) -> None:
    is_running = await video_generation_model.is_running(
        session_id="session_123",
        run_context=run_context,
    )

    assert is_running is False


async def test_video_generation_model_get(
    run_context: RunContext, video_generation_model: VideoGenerationModel
) -> None:
    result = await video_generation_model.get(
        session_id="session_123",
        run_context=run_context,
    )

    assert result.video_mime_blob.mime_type == "video/mp4"


async def test_video_generation_model_delete(
    run_context: RunContext, video_generation_model: VideoGenerationModel
) -> None:
    # Should not raise any exception
    await video_generation_model.delete(
        session_id="session_123",
        run_context=run_context,
    )
