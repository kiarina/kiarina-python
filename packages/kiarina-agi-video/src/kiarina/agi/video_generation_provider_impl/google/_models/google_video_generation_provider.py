import asyncio
import logging
import math
from typing import Any

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

from .._settings import GoogleVideoGenerationProviderSettings

try:
    from google import genai
    from google.genai import types

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-google and google-genai are required to use "
        "GoogleVideoGenerationProvider. Install them with: "
        "pip install 'kiarina-agi-video[video-generation-provider-google]'"
    ) from exc

logger = logging.getLogger(__name__)


class GoogleVideoGenerationProvider(BaseVideoGenerationProvider):
    """
    Google Veo Video Provider Implementation
    """

    def __init__(self, settings: GoogleVideoGenerationProviderSettings) -> None:
        super().__init__()

        self.settings: GoogleVideoGenerationProviderSettings = settings
        self._client: genai.Client | None = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"

    @property
    def google_auth_settings(self) -> kiarina.lib.google.GoogleSettings:
        return kiarina.lib.google.settings_manager.get_settings(
            self.settings.google_auth_settings_key
        )

    @property
    def credentials(self) -> kiarina.lib.google.Credentials:
        return kiarina.lib.google.get_credentials(
            settings=self.google_auth_settings,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                credentials=self.credentials,
                http_options=types.HttpOptions(
                    timeout=self.settings.timeout_milliseconds
                ),
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
        config_kwargs: dict[str, Any] = {
            "aspect_ratio": self.settings.aspect_ratio,
            "resolution": self.settings.resolution,
            "duration_seconds": self.settings.duration_seconds,
        }

        if self.settings.negative_prompt:
            config_kwargs["negative_prompt"] = self.settings.negative_prompt

        # Handle first frame image
        if first_image_file_path:
            file_blob = await read_file(first_image_file_path)

            if not file_blob:
                raise ValueError(f"File not found: {first_image_file_path}")

            config_kwargs["image"] = types.Part.from_bytes(
                data=file_blob.raw_data, mime_type=file_blob.mime_type
            )

        # Handle last frame image
        if self.settings.last_image_file_path:
            file_blob = await read_file(self.settings.last_image_file_path)

            if not file_blob:
                raise ValueError(
                    f"File not found: {self.settings.last_image_file_path}"
                )

            config_kwargs["last_frame"] = types.Part.from_bytes(
                data=file_blob.raw_data, mime_type=file_blob.mime_type
            )

        # Handle reference images (max 3)
        if self.settings.reference_images:
            reference_images: list[types.VideoGenerationReferenceImage] = []

            for ref_path in self.settings.reference_images[:3]:
                file_blob = await read_file(ref_path)

                if not file_blob:
                    raise ValueError(f"File not found: {ref_path}")

                reference_images.append(
                    types.VideoGenerationReferenceImage(
                        image=types.Image(
                            image_bytes=file_blob.raw_data,
                            mime_type=file_blob.mime_type,
                        ),
                        reference_type=types.VideoGenerationReferenceType.ASSET,
                    )
                )

            if reference_images:
                config_kwargs["reference_images"] = reference_images

        try:
            operation = await asyncio.to_thread(
                self.client.models.generate_videos,
                model=self.settings.model_name,
                prompt=prompt,
                config=types.GenerateVideosConfig(**config_kwargs),
            )

            if not operation.name:
                raise RuntimeError("Failed to get operation name")

            session_id: VideoGenerationSessionID = operation.name
            logger.info(f"Started video generation: {session_id}")

            cost_recorder.add(self._build_cost_record())

            return session_id

        except Exception as e:
            raise RuntimeError(f"Failed to create video: {e}") from e

    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        raise NotImplementedError("Google Veo does not support video editing")

    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        operation = types.GenerateVideosOperation()
        operation.name = session_id

        operation = await asyncio.to_thread(
            self.client.operations.get,
            operation,
        )

        if not operation.response:
            raise RuntimeError("Failed to get operation response for extension")

        if not operation.response.generated_videos:
            raise RuntimeError("No generated videos found for extension")

        config_kwargs: dict[str, Any] = {
            "resolution": self.settings.resolution,
        }

        if self.settings.negative_prompt:
            config_kwargs["negative_prompt"] = self.settings.negative_prompt

        operation = await asyncio.to_thread(
            self.client.models.generate_videos,
            model=self.settings.model_name,
            video=operation.response.generated_videos[0].video,
            prompt=prompt,
            config=types.GenerateVideosConfig(**config_kwargs),
        )

        if not operation.name:
            raise RuntimeError("Failed to get operation name")

        new_session_id: VideoGenerationSessionID = operation.name
        logger.info(f"Started video extension: {new_session_id}")

        cost_recorder.add(self._build_cost_record())

        return new_session_id

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool:
        try:
            operation = types.GenerateVideosOperation()
            operation.name = session_id

            operation = await asyncio.to_thread(
                self.client.operations.get,
                operation,
            )

            return not operation.done

        except Exception as e:
            logger.error(f"Failed to check operation status: {e}")
            return False

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult:
        operation = types.GenerateVideosOperation()
        operation.name = session_id

        operation = await asyncio.to_thread(
            self.client.operations.get,
            operation,
        )

        if not operation.done:
            raise RuntimeError(f"Video {session_id} is still being generated.")

        if operation.error:
            raise RuntimeError(f"Video generation failed: {operation.error}")

        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError("No video generated")

        video = operation.response.generated_videos[0]

        if not video.video:
            raise RuntimeError("No video file in response")

        video_data = await asyncio.to_thread(
            self.client.files.download,
            file=video.video,
        )

        video_mime_blob = MIMEBlob(
            mime_type="video/mp4",
            raw_data=video_data,
        )

        return VideoGenerationResult(video_mime_blob=video_mime_blob)

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None:
        try:
            operation = types.GenerateVideosOperation()
            operation.name = session_id

            operation = await asyncio.to_thread(
                self.client.operations.get,
                operation,
            )

            if (
                not operation.done
                or not operation.response
                or not operation.response.generated_videos
                or not operation.response.generated_videos[0].video
                or not operation.response.generated_videos[0].video.uri
            ):
                return

            await asyncio.to_thread(
                self.client.files.delete,
                name=operation.response.generated_videos[0].video.uri,
            )

            logger.info(f"Deleted video operation: {session_id}")

        except Exception as e:
            logger.error(f"Failed to delete video {session_id}: {e}")

    def _build_cost_record(self) -> CostRecord:
        duration_seconds = int(self.settings.duration_seconds)
        duration_cost = self.settings.cost_microdollars_per_second

        cost = math.ceil(duration_cost * duration_seconds)

        return CostRecord(
            microdollars=cost,
            kind="video",
            source="google",
            metadata={
                "model_name": self.settings.model_name,
                "duration_seconds": duration_seconds,
            },
        )
