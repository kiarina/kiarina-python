from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider import BaseTextEmbeddingProvider

from .._settings import GoogleTextEmbeddingProviderSettings

try:
    import numpy as np
    from google import genai
    from google.genai import types

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai, kiarina-lib-google, and numpy are required to use "
        "GoogleTextEmbeddingProvider. "
        "Install them with: pip install 'kiarina-agi-text[text-embedding-provider-google]'"
    ) from exc


class GoogleTextEmbeddingProvider(BaseTextEmbeddingProvider):
    def __init__(self, settings: GoogleTextEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: GoogleTextEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._client: genai.Client | None = None

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

        if self.settings.backend_type == "vertex_ai_api_key":
            backend_config: dict[str, Any] = {
                "api_key": self.api_key,
                "project": self.google_auth_settings.project_id,
                "vertexai": True,
            }

            if self.settings.vertex_ai_location:
                backend_config["location"] = self.settings.vertex_ai_location

            return backend_config

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

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind=self.settings.kind,
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
        )

    async def _embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        space = self.get_space()
        chunks = self._split_text(text)
        vectors: list[np.ndarray] = []
        weights: list[int] = []

        for chunk in chunks:
            response = await self.client.aio.models.embed_content(
                model=self.settings.model_name,
                contents=chunk,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.settings.dimension,
                    task_type=self.settings.task_type,
                ),
            )

            embeddings = response.embeddings

            if not embeddings or embeddings[0].values is None:
                raise ValueError("Google returned no embedding for the text.")

            vectors.append(
                np.asarray(embeddings[0].values, dtype=np.float32).reshape(-1)
            )
            weights.append(max(1, len(chunk)))

        vector = self._merge_vectors(vectors, weights)

        if self.normalize_embedding:
            vector = l2_normalize(vector)

        cost_recorder.add(
            CostRecord(
                microdollars=self.settings.cost_microdollars_per_request * len(chunks),
                kind="text_embedding",
                source=self.name,
                metadata={
                    "model_name": self.settings.model_name,
                    "request_count": len(chunks),
                    "output_dimensionality": self.settings.dimension,
                },
            )
        )

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=vector,
            metadata={
                "model_name": self.settings.model_name,
                "text_length": len(text),
                "chunk_count": len(chunks),
            },
        )

    def _split_text(self, text: str) -> list[str]:
        max_chars = self.settings.max_char_count

        if len(text) <= max_chars:
            return [text]

        chunks = [
            text[index : index + max_chars] for index in range(0, len(text), max_chars)
        ]
        return [chunk for chunk in chunks if chunk]

    def _merge_vectors(
        self, vectors: list[np.ndarray], weights: list[int]
    ) -> np.ndarray:
        if len(vectors) == 1:
            return vectors[0]

        merged = np.average(np.stack(vectors), axis=0, weights=np.asarray(weights))
        return np.asarray(merged, dtype=np.float32)

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"google-text:model={self.settings.model_name}:"
            f"dim={self.settings.dimension}:norm={norm}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"
