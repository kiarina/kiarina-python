import base64

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.image_embedding_provider import (
    BaseImageEmbeddingProvider,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._settings import Qwen3VLImageEmbeddingProviderSettings

try:
    import cv2
    import httpx
except ImportError as exc:
    raise ImportError(
        "httpx and opencv-python are required to use "
        "Qwen3VLImageEmbeddingProvider. "
        "Install them with: pip install 'kiarina-agi-image[image-embedding-provider-qwen3-vl]'"
    ) from exc


class Qwen3VLImageEmbeddingProvider(BaseImageEmbeddingProvider):
    def __init__(self, settings: Qwen3VLImageEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: Qwen3VLImageEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind=self.settings.kind,
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
        )

    async def _embed(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        space = self.get_space()

        image_base64 = _encode_png(pixels)

        async with httpx.AsyncClient(
            base_url=self.settings.base_url, timeout=self.settings.timeout
        ) as client:
            response = await client.post(
                "/embed",
                json={
                    "image_base64": image_base64,
                    "model_id": self.settings.model_id,
                },
            )
            response.raise_for_status()
            payload = response.json()

        embedding = np.asarray(payload["embedding"], dtype=np.float32).reshape(-1)

        if self.normalize_embedding:
            embedding = l2_normalize(embedding)

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=embedding,
            metadata={
                "model_id": self.settings.model_id,
                "height": int(pixels.shape[0]),
                "width": int(pixels.shape[1]),
            },
        )

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"qwen3-vl:model={self.settings.model_id}:"
            f"dim={self.settings.dimension}:norm={norm}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.base_url})"


def _encode_png(pixels: ImagePixels) -> str:
    bgr = np.ascontiguousarray(pixels[..., ::-1])
    success, buffer = cv2.imencode(".png", bgr)

    if not success:  # pragma: no cover
        raise ValueError("Failed to encode image as PNG.")

    return base64.b64encode(buffer.tobytes()).decode("ascii")
