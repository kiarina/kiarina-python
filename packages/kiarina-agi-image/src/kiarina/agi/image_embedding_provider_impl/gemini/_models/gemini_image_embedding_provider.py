import io
from typing import Any

import numpy as np

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.image_embedding_provider import (
    BaseImageEmbeddingProvider,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._settings import GeminiImageEmbeddingProviderSettings

try:
    from google import genai
    from google.genai import types
    from PIL import Image

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai, kiarina-lib-google-auth, and pillow are required to use "
        "GeminiImageEmbeddingProvider. "
        "Install them with: pip install 'kiarina-agi-image[image-embedding-provider-gemini]'"
    ) from exc


class GeminiImageEmbeddingProvider(BaseImageEmbeddingProvider):
    def __init__(self, settings: GeminiImageEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: GeminiImageEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._client: genai.Client | None = None

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def google_auth_settings(self) -> kiarina.lib.google.GoogleSettings:
        return kiarina.lib.google.settings_manager.get_settings(
            self.settings.google_auth_settings_key
        )

    @property
    def credentials(self) -> kiarina.lib.google.Credentials:
        return kiarina.lib.google.get_credentials(
            settings=self.google_auth_settings,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    @property
    def api_key(self) -> str | None:
        api_key = self.google_auth_settings.api_key
        return api_key.get_secret_value() if api_key is not None else None

    @property
    def backend_config(self) -> dict[str, Any]:
        if self.settings.backend_type == "gemini_api":
            if self.api_key is not None:
                return {"api_key": self.api_key}

            return {}

        elif self.settings.backend_type == "vertex_ai_api_key":
            backend_config: dict[str, Any] = {
                "api_key": self.api_key,
                "project": self.google_auth_settings.project_id,
                "vertexai": True,
            }

            if self.settings.vertex_ai_location:
                backend_config["location"] = self.settings.vertex_ai_location

            return backend_config

        else:
            backend_config = {
                "vertexai": True,
                "credentials": self.credentials,
                "project": self.google_auth_settings.project_id,
            }

            if self.settings.vertex_ai_location:
                backend_config["location"] = self.settings.vertex_ai_location

            return backend_config

    @property
    def client(self) -> "genai.Client":
        if self._client is None:
            self._client = genai.Client(**self.backend_config)

        return self._client

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind=self.settings.kind,
            space_id=self._embedding_space_id(),
            dimension=self.settings.output_dimensionality,
        )

    async def _embed(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        space = self.get_space()

        config = types.EmbedContentConfig(
            output_dimensionality=self.settings.output_dimensionality,
            task_type=self.settings.task_type,
        )

        content = types.Content(
            parts=[
                types.Part.from_bytes(data=_encode_png(pixels), mime_type="image/png")
            ]
        )

        response = await self.client.aio.models.embed_content(
            model=self.settings.model_name,
            contents=content,
            config=config,
        )

        embeddings = response.embeddings

        if not embeddings or embeddings[0].values is None:
            raise ValueError("Gemini returned no embedding for the image.")

        vector = np.asarray(embeddings[0].values, dtype=np.float32).reshape(-1)

        if self.normalize_embedding:
            vector = l2_normalize(vector)

        cost_recorder.add(
            CostRecord(
                microdollars=self.settings.cost_microdollars_per_request,
                kind="image_embedding",
                source=self.name,
                metadata={
                    "model_name": self.settings.model_name,
                    "output_dimensionality": self.settings.output_dimensionality,
                },
            )
        )

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=vector,
            metadata={
                "model_name": self.settings.model_name,
                "height": int(pixels.shape[0]),
                "width": int(pixels.shape[1]),
            },
        )

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"gemini-embedding-2:model={self.settings.model_name}:"
            f"dim={self.settings.output_dimensionality}:norm={norm}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"


def _encode_png(pixels: ImagePixels) -> bytes:
    buffer = io.BytesIO()
    Image.fromarray(pixels).save(buffer, format="PNG")
    return buffer.getvalue()
