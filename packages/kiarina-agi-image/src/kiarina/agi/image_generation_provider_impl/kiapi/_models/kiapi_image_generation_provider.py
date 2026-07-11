import os
from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider import (
    BaseImageGenerationProvider,
    ImageGenerationResult,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file
from kiarina.utils.mime import MIMEBlob

from .._settings import KiapiImageGenerationProviderSettings

try:
    import httpx
except ImportError as exc:
    raise ImportError(
        "httpx is required to use KiapiImageGenerationProvider. "
        "Install it with: pip install "
        "'kiarina-agi-image[image-generation-provider-kiapi]'"
    ) from exc


class KiapiImageGenerationProvider(BaseImageGenerationProvider):
    def __init__(self, settings: KiapiImageGenerationProviderSettings) -> None:
        super().__init__()
        self.settings = settings

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self.settings.kiapi_base_url}, family={self.settings.family})"
        )

    async def _generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        output_format = self.settings.extra_params.get("format", "png")
        if output_format not in {"png", "jpeg", "webp"}:
            raise ValueError("extra_params.format must be png, jpeg, or webp.")

        async with httpx.AsyncClient(
            base_url=self.settings.kiapi_base_url.rstrip("/"),
            timeout=self.settings.timeout,
        ) as client:
            if file_paths:
                response = await self._edit(client, prompt, file_paths, output_format)
            else:
                response = await client.post(
                    f"/v1/image/{self.settings.family}/generate",
                    headers={"Accept": f"image/{output_format}"},
                    json=self._build_payload(prompt),
                )

            response.raise_for_status()

        mime_type = response.headers.get(
            "content-type", f"image/{output_format}"
        ).split(";", 1)[0]
        return ImageGenerationResult(
            mime_blob=MIMEBlob(mime_type=mime_type, raw_data=response.content)
        )

    async def _edit(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        file_paths: list[str],
        output_format: str,
    ) -> httpx.Response:
        if self.settings.family == "ernie" and len(file_paths) != 1:
            raise ValueError("The ernie family accepts exactly one input image.")

        images = [
            await self._upload_image(client, file_path) for file_path in file_paths
        ]
        image_params: dict[str, Any]
        if self.settings.family == "ernie":
            image_params = {"image": images[0]}
        else:
            image_params = {"images": images}

        return await client.post(
            f"/v1/image/{self.settings.family}/edit",
            headers={"Accept": f"image/{output_format}"},
            json={**self._build_payload(prompt), **image_params},
        )

    async def _upload_image(
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

    def _build_payload(self, prompt: str) -> dict[str, Any]:
        return {**self.settings.extra_params, "mode": "sync", "prompt": prompt}
