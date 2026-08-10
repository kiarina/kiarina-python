import logging
from io import BytesIO

from PIL import Image

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider import (
    BaseImageGenerationProvider,
    ImageGenerationResult,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.mime import MIMEBlob

from .._settings import MockImageGenerationProviderSettings

logger = logging.getLogger(__name__)


class MockImageGenerationProvider(BaseImageGenerationProvider):
    """
    Mock Image Provider Implementation for Testing
    """

    def __init__(self, settings: MockImageGenerationProviderSettings) -> None:
        super().__init__()

        self.settings: MockImageGenerationProviderSettings = settings

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"

    async def _generate(
        self,
        prompt: str,
        *,
        file_paths: list[str] | None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageGenerationResult:
        logger.info(f"Mock image generation: {prompt} (files: {len(file_paths or [])})")

        color = self.settings.color
        if file_paths:
            color = (
                color[2],
                color[0],
                color[1],
            )

        image = Image.new(
            "RGB",
            (self.settings.image_width, self.settings.image_height),
            color=color,
        )

        buffer = BytesIO()
        image.save(buffer, format=self.settings.output_format.upper())
        image_bytes = buffer.getvalue()

        mime_blob = MIMEBlob(
            mime_type=f"image/{self.settings.output_format}",
            raw_data=image_bytes,
        )

        return ImageGenerationResult(mime_blob=mime_blob)
