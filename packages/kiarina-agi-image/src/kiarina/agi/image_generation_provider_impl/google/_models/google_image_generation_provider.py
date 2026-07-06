import logging
import math
from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider import (
    BaseImageGenerationProvider,
    ImageGenerationResult,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file
from kiarina.utils.mime import MIMEBlob, detect_mime_type

from .._settings import GoogleImageGenerationProviderSettings

try:
    from google import genai
    from google.genai import types

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai and kiarina-lib-google-auth are required to use "
        "GoogleImageGenerationProvider. "
        "Install them with: pip install 'kiarina-agi-image[image-generation-provider-google]'"
    ) from exc

logger = logging.getLogger(__name__)


class GoogleImageGenerationProvider(BaseImageGenerationProvider):
    """
    Google Gemini Image Provider Implementation
    """

    def __init__(self, settings: GoogleImageGenerationProviderSettings) -> None:
        super().__init__()

        self.settings: GoogleImageGenerationProviderSettings = settings
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
            self._client = genai.Client(credentials=self.credentials)

        return self._client

    async def _generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        contents: list[Any] = [prompt]

        for file_path in file_paths or []:
            file_blob = await read_file(file_path)

            if not file_blob:
                raise ValueError(f"{file_path} does not exist.")

            contents.append(
                types.Part.from_bytes(
                    data=file_blob.raw_data, mime_type=file_blob.mime_type
                )
            )

        response = self.client.models.generate_content(
            model=self.settings.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=self.settings.aspect_ratio,
                    image_size=self.settings.image_size,
                ),
            ),
        )

        image_data: bytes | None = None

        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    break

        if not image_data:
            raise RuntimeError("Failed to generate image data")

        mime_type = detect_mime_type(raw_data=image_data)

        mime_blob = MIMEBlob(
            mime_type=mime_type or "image/png",
            raw_data=image_data,
        )

        cost_recorder.add(self._build_cost_record(response))

        return ImageGenerationResult(mime_blob=mime_blob)

    def _build_cost_record(self, response: types.GenerateContentResponse) -> CostRecord:
        input_tokens = 0
        output_text_tokens = 0
        output_image_tokens = 0

        if response.usage_metadata:
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_text_tokens = response.usage_metadata.thoughts_token_count or 0
            output_image_tokens = response.usage_metadata.candidates_token_count or 0

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        output_text_cost = self.settings.output_text_cost_microdollars_per_1k_tokens
        output_image_cost = self.settings.output_image_cost_microdollars_per_1k_tokens

        cost = math.ceil(
            (input_tokens / 1000) * input_cost
            + (output_text_tokens / 1000) * output_text_cost
            + (output_image_tokens / 1000) * output_image_cost
        )

        return CostRecord(
            microdollars=cost,
            kind="image",
            source="google",
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "output_text_tokens": output_text_tokens,
                "output_image_tokens": output_image_tokens,
            },
        )
