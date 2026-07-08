import logging
import math

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider import (
    BaseVideoGenerationProvider,
    VideoGenerationResult,
    VideoGenerationSessionID,
)
from kiarina.utils.file.asyncio import read_file
from kiarina.utils.mime import MIMEBlob

from .._settings import OpenAIVideoGenerationProviderSettings
from .._utils.resize_image_to_target_size import resize_image_to_target_size

try:
    from openai import AsyncClient, NotFoundError

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-openai and openai are required to use "
        "OpenAIVideoGenerationProvider. Install them with: "
        "pip install 'kiarina-agi-video[video-generation-provider-openai]'"
    ) from exc

logger = logging.getLogger(__name__)


class OpenAIVideoGenerationProvider(BaseVideoGenerationProvider):
    """
    OpenAI Video Provider Implementation
    """

    def __init__(self, settings: OpenAIVideoGenerationProviderSettings) -> None:
        super().__init__()

        self.settings: OpenAIVideoGenerationProviderSettings = settings
        self._client: AsyncClient | None = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"

    @property
    def openai_settings(self) -> kiarina.lib.openai.OpenAISettings:
        return kiarina.lib.openai.settings_manager.get_settings(
            self.settings.openai_settings_key
        )

    @property
    def client(self) -> AsyncClient:
        if self._client is None:
            self._client = AsyncClient(
                timeout=self.settings.timeout,
                **self.openai_settings.to_client_kwargs(),
            )

        return self._client

    async def _create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        if first_image_file_path:
            file_blob = await read_file(first_image_file_path)

            if not file_blob:
                raise ValueError(
                    f"File not found or inaccessible: {first_image_file_path}"
                )

            # Resize image to target size
            resized_data = resize_image_to_target_size(
                file_blob.raw_data, self.settings.size
            )

            video = await self.client.videos.create(
                prompt=prompt,
                input_reference=("reference.jpg", resized_data, "image/jpeg"),
                model=self.settings.model_name,
                size=self.settings.size,
                seconds=self.settings.seconds,
            )
        else:
            video = await self.client.videos.create(
                prompt=prompt,
                model=self.settings.model_name,
                size=self.settings.size,
                seconds=self.settings.seconds,
            )

        logger.info(f"Created video: {video.id}")

        cost_recorder.add(self._build_cost_record())

        return video.id

    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        remix_video = await self.client.videos.remix(
            session_id,
            prompt=prompt,
        )

        logger.info(f"Remixed video: {remix_video.id}")

        cost_recorder.add(self._build_cost_record())

        return remix_video.id

    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        raise NotImplementedError("OpenAI does not support video extension")

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool:
        try:
            video = await self.client.videos.retrieve(session_id)
            return video.status in ["queued", "in_progress"]

        except NotFoundError:
            return False

        except Exception:
            raise

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult:
        try:
            video = await self.client.videos.retrieve(session_id)

        except NotFoundError as e:
            raise ValueError(f"Video not found: {session_id}") from e

        except Exception:
            raise

        if video.status in ["queued", "in_progress"]:
            raise RuntimeError(
                f"Video {session_id} is still being generated. "
                "Please wait until it completes before calling get()."
            )

        if video.status == "failed":
            # Delete the failed video before throwing an exception
            await self.delete(session_id, run_context=run_context)
            error_msg = f"Video generation failed: {video.error}"
            raise RuntimeError(error_msg)

        # If status is completed, download the video
        video_content = await self.client.videos.download_content(
            video.id, variant="video"
        )
        thumbnail_content = await self.client.videos.download_content(
            video.id, variant="thumbnail"
        )
        spritesheet_content = await self.client.videos.download_content(
            video.id, variant="spritesheet"
        )

        video_mime_blob = MIMEBlob(
            mime_type="video/mp4",
            raw_data=video_content.read(),
        )

        thumbnail_mime_blob = MIMEBlob(
            mime_type="image/webp",
            raw_data=thumbnail_content.read(),
        )

        spritesheet_mime_blob = MIMEBlob(
            mime_type="image/jpeg",
            raw_data=spritesheet_content.read(),
        )

        return VideoGenerationResult(
            video_mime_blob=video_mime_blob,
            thumbnail_mime_blob=thumbnail_mime_blob,
            spritesheet_mime_blob=spritesheet_mime_blob,
        )

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None:
        try:
            await self.client.videos.delete(session_id)
            logger.info(f"Deleted video: {session_id}")

        except NotFoundError:
            pass

        except Exception as e:
            logger.error(f"Failed to delete video {session_id}: {e}")

    def _build_cost_record(self) -> CostRecord:
        seconds = int(self.settings.seconds)
        size = self.settings.size

        if size in ["1280x720", "720x1280"]:
            cost_per_second = self.settings.cost_microdollars_720p_per_second
        else:
            cost_per_second = self.settings.cost_microdollars_1024p_per_second

        cost = math.ceil(cost_per_second * seconds)

        return CostRecord(
            microdollars=cost,
            kind="video",
            source="openai",
            metadata={
                "model_name": self.settings.model_name,
                "size": size,
                "seconds": seconds,
            },
        )
