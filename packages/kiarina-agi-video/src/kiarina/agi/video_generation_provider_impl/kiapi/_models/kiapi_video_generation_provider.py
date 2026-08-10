import os
from typing import Any, cast

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider import (
    BaseVideoGenerationProvider,
    VideoGenerationResult,
    VideoGenerationSessionID,
)
from kiarina.utils.file.asyncio import read_file
from kiarina.utils.mime import MIMEBlob

from .._settings import KiapiVideoGenerationProviderSettings

try:
    import httpx
except ImportError as exc:
    raise ImportError(
        "httpx is required to use KiapiVideoGenerationProvider. "
        "Install it with: pip install "
        "'kiarina-agi-video[video-generation-provider-kiapi]'"
    ) from exc


class KiapiVideoGenerationProvider(BaseVideoGenerationProvider):
    def __init__(self, settings: KiapiVideoGenerationProviderSettings) -> None:
        super().__init__()
        self.settings = settings

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self.settings.kiapi_base_url}, family={self.settings.family})"
        )

    async def _create(
        self,
        prompt: str,
        *,
        first_image_file_path: str | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        async with self._create_client() as client:
            payload = {**self.settings.extra_params, "mode": "async", "prompt": prompt}
            if first_image_file_path:
                payload["image"] = await self._upload_file(
                    client, first_image_file_path
                )

            response = await client.post(
                f"/v1/video/{self.settings.family}/generate",
                headers={"Accept": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            session_id: VideoGenerationSessionID = response.json()["job_id"]
            return session_id

    async def _edit(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        raise NotImplementedError("kiapi video editing is not supported.")

    async def _extend(
        self,
        prompt: str,
        *,
        session_id: VideoGenerationSessionID,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> VideoGenerationSessionID:
        raise NotImplementedError("kiapi video extension is not supported.")

    async def is_running(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> bool:
        async with self._create_client() as client:
            job = await self._get_job(client, session_id)
        return job["status"] in {"queued", "running"}

    async def get(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> VideoGenerationResult:
        async with self._create_client() as client:
            job = await self._get_job(client, session_id)
            status = job["status"]
            if status in {"queued", "running"}:
                raise RuntimeError(f"Video {session_id} is still being generated.")
            if status != "succeeded":
                raise RuntimeError(
                    f"Video generation failed: {job.get('error') or status}"
                )

            file_id = self._get_result_file_id(job)
            response = await client.get(f"/v1/files/{file_id}/download")
            response.raise_for_status()

        mime_type = response.headers.get("content-type", "video/mp4").split(";", 1)[0]
        return VideoGenerationResult(
            video_mime_blob=MIMEBlob(mime_type=mime_type, raw_data=response.content)
        )

    async def delete(
        self,
        session_id: VideoGenerationSessionID,
        *,
        run_context: RunContext,
    ) -> None:
        async with self._create_client() as client:
            response = await client.delete(f"/v1/jobs/{session_id}")
            response.raise_for_status()

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.settings.kiapi_base_url.rstrip("/"),
            timeout=self.settings.timeout,
        )

    async def _upload_file(
        self, client: httpx.AsyncClient, file_path: str
    ) -> dict[str, str]:
        file_blob = await read_file(file_path)
        if not file_blob:
            raise ValueError(f"{file_path} does not exist.")

        response = await client.post(
            "/v1/files",
            files={
                "file": (
                    os.path.basename(file_path),
                    file_blob.raw_data,
                    file_blob.mime_type,
                )
            },
        )
        response.raise_for_status()
        return {"type": "file_id", "file_id": response.json()["file_id"]}

    async def _get_job(
        self, client: httpx.AsyncClient, session_id: VideoGenerationSessionID
    ) -> dict[str, Any]:
        response = await client.get(f"/v1/jobs/{session_id}")
        response.raise_for_status()
        job: dict[str, Any] = response.json()
        return job

    def _get_result_file_id(self, job: dict[str, Any]) -> str:
        result = job.get("result")
        if isinstance(result, dict) and isinstance(result.get("file_id"), str):
            return cast(str, result["file_id"])

        artifacts = job.get("artifacts")
        if isinstance(artifacts, list) and artifacts and isinstance(artifacts[0], str):
            return artifacts[0]

        raise RuntimeError("Video generation produced no video artifact.")
