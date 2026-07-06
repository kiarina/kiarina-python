import base64
import logging
import math
import os
from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider import (
    BaseImageGenerationProvider,
    ImageGenerationResult,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file
from kiarina.utils.mime import MIMEBlob

from .._settings import OpenAIImageGenerationProviderSettings

try:
    import httpx

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "httpx and kiarina-lib-openai are required to use OpenAIImageGenerationProvider. "
        "Install them with: pip install 'kiarina-agi-image[image-generation-provider-openai]'"
    ) from exc

logger = logging.getLogger(__name__)


class OpenAIImageGenerationProvider(BaseImageGenerationProvider):
    """
    OpenAI Image Provider Implementation
    """

    def __init__(self, settings: OpenAIImageGenerationProviderSettings) -> None:
        super().__init__()

        self.settings: OpenAIImageGenerationProviderSettings = settings

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"

    @property
    def openai_settings(self) -> kiarina.lib.openai.OpenAISettings:
        return kiarina.lib.openai.settings_manager.get_settings(
            self.settings.openai_settings_key
        )

    @property
    def api_key(self) -> str:
        if self.openai_settings.api_key:
            return self.openai_settings.api_key.get_secret_value()
        elif os.getenv("OPENAI_API_KEY"):
            return os.getenv("OPENAI_API_KEY", "")
        else:
            raise ValueError("OpenAI API key is not set.")

    async def _generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        all_file_paths = [*self.settings.base_file_paths, *(file_paths or [])]

        if all_file_paths:
            return await self._generate_with_images(
                prompt,
                file_paths=all_file_paths,
                cost_recorder=cost_recorder,
                run_context=run_context,
            )

        return await self._generate_without_images(
            prompt,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    async def _generate_without_images(
        self,
        prompt: str,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        url = "https://api.openai.com/v1/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.settings.model_name,
            "prompt": prompt,
            "n": 1,
            "background": self.settings.background,
            "output_format": self.settings.output_format,
            "quality": self.settings.quality,
            "size": self.settings.size,
        }

        async with httpx.AsyncClient(timeout=self.settings.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        b64_json = data["data"][0]["b64_json"]
        image_bytes = base64.b64decode(b64_json)

        mime_blob = MIMEBlob(
            mime_type=f"image/{self.settings.output_format}",
            raw_data=image_bytes,
        )

        cost_recorder.add(self._build_cost_record(data))

        return ImageGenerationResult(mime_blob=mime_blob)

    async def _generate_with_images(
        self,
        prompt: str,
        *,
        file_paths: list[str],
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        url = "https://api.openai.com/v1/images/edits"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        image_files: list[Any] = []

        for file_path in file_paths:
            file_blob = await read_file(file_path)

            if not file_blob:
                raise ValueError(f"{file_path} does not exist.")

            image_files.append(
                (
                    os.path.basename(file_path),
                    file_blob.raw_data,
                    file_blob.mime_type,
                )
            )

        mask_file: Any = None

        if self.settings.mask_file_path:
            file_blob = await read_file(self.settings.mask_file_path)

            if not file_blob:
                raise ValueError(f"{self.settings.mask_file_path} does not exist.")

            mask_file = (
                os.path.basename(self.settings.mask_file_path),
                file_blob.raw_data,
                file_blob.mime_type,
            )

        # Request data for multipart/form-data
        request_data = {
            "model": self.settings.model_name,
            "prompt": prompt,
            "quality": self.settings.quality,
            "size": self.settings.size,
        }

        request_files: list[Any] = []

        for image_file in image_files:
            request_files.append(("image[]", image_file))

        if mask_file:
            request_files.append(("mask", mask_file))

        async with httpx.AsyncClient(timeout=self.settings.timeout) as client:
            response = await client.post(
                url, headers=headers, data=request_data, files=request_files
            )
            response.raise_for_status()
            response_json = response.json()

        b64_json = response_json["data"][0]["b64_json"]
        image_bytes = base64.b64decode(b64_json)

        mime_blob = MIMEBlob(
            mime_type=f"image/{self.settings.output_format}",
            raw_data=image_bytes,
        )

        cost_recorder.add(self._build_cost_record(response_json))

        return ImageGenerationResult(mime_blob=mime_blob)

    def _build_cost_record(self, response_json: dict[str, Any]) -> CostRecord:
        input_text_tokens = 0
        input_image_tokens = 0
        output_image_tokens = 0

        if usage := response_json.get("usage"):
            if isinstance(usage, dict):
                if input_tokens_details := usage.get("input_tokens_details"):
                    if isinstance(input_tokens_details, dict):
                        input_text_tokens = input_tokens_details.get("text_tokens", 0)
                        input_image_tokens = input_tokens_details.get("image_tokens", 0)

                output_image_tokens = usage.get("output_tokens", 0)

        input_text_cost = self.settings.input_text_cost_microdollars_per_1k_tokens
        input_image_cost = self.settings.input_image_cost_microdollars_per_1k_tokens
        output_image_cost = self.settings.output_image_cost_microdollars_per_1k_tokens

        cost = math.ceil(
            input_text_cost * input_text_tokens / 1_000
            + input_image_cost * input_image_tokens / 1_000
            + output_image_cost * output_image_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="image",
            source="openai",
            metadata={
                "model_name": self.settings.model_name,
                "input_text_tokens": input_text_tokens,
                "input_image_tokens": input_image_tokens,
                "output_image_tokens": output_image_tokens,
            },
        )
