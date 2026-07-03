import math
from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_provider import BaseTextEmbeddingProvider

from .._settings import OpenAITextEmbeddingProviderSettings

try:
    import numpy as np
    import tiktoken
    from openai import AsyncOpenAI

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-openai, numpy, openai, and tiktoken are required to use "
        "OpenAITextEmbeddingProvider. "
        "Install them with: pip install 'kiarina-agi-text[text-embedding-provider-openai]'"
    ) from exc


class OpenAITextEmbeddingProvider(BaseTextEmbeddingProvider):
    def __init__(self, settings: OpenAITextEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: OpenAITextEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._client: AsyncOpenAI | None = None

    @property
    def openai_settings(self) -> kiarina.lib.openai.OpenAISettings:
        return kiarina.lib.openai.settings_manager.get_settings(
            self.settings.openai_settings_key
        )

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                timeout=self.settings.timeout,
                **self.openai_settings.to_client_kwargs(),
            )

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
        prompt_tokens = 0

        for chunk in chunks:
            response = await self.client.embeddings.create(
                input=chunk,
                model=self.settings.model_name,
            )

            if not response.data:
                raise ValueError("OpenAI returned no embedding for the text.")

            vector = np.asarray(response.data[0].embedding, dtype=np.float32).reshape(
                -1
            )
            vectors.append(vector)
            weights.append(max(1, self._count_tokens(chunk)))
            prompt_tokens += self._extract_prompt_tokens(response, chunk)

        embedding = self._merge_vectors(vectors, weights)

        if self.normalize_embedding:
            embedding = l2_normalize(embedding)

        if prompt_tokens:
            cost_recorder.add(self._build_cost_record(prompt_tokens))

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=embedding,
            metadata={
                "model_name": self.settings.model_name,
                "text_length": len(text),
                "chunk_count": len(chunks),
                "prompt_tokens": prompt_tokens,
            },
        )

    def _split_text(self, text: str) -> list[str]:
        token_count = self._count_tokens(text)

        if token_count <= self.settings.max_token_count:
            return [text]

        max_chars = max(
            1, math.floor(len(text) * self.settings.max_token_count / token_count)
        )
        chunks = [
            text[index : index + max_chars] for index in range(0, len(text), max_chars)
        ]
        return [chunk for chunk in chunks if chunk]

    def _count_tokens(self, text: str) -> int:
        if not text:
            return 0

        try:
            encoding = tiktoken.encoding_for_model(self.settings.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("o200k_base")

        return len(encoding.encode(text, allowed_special="all", disallowed_special=()))

    def _extract_prompt_tokens(self, response: Any, text: str) -> int:
        if hasattr(response, "usage") and response.usage:
            if hasattr(response.usage, "prompt_tokens"):
                return int(response.usage.prompt_tokens)

            if hasattr(response.usage, "total_tokens"):
                return int(response.usage.total_tokens)

        return self._count_tokens(text)

    def _merge_vectors(
        self, vectors: list[np.ndarray], weights: list[int]
    ) -> np.ndarray:
        if len(vectors) == 1:
            return vectors[0]

        merged = np.average(np.stack(vectors), axis=0, weights=np.asarray(weights))
        return np.asarray(merged, dtype=np.float32)

    def _build_cost_record(self, prompt_tokens: int) -> CostRecord:
        microdollars = math.ceil(
            self.settings.cost_microdollars_per_1k_tokens * prompt_tokens / 1_000
        )

        return CostRecord(
            microdollars=microdollars,
            kind="text_embedding",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "prompt_tokens": prompt_tokens,
                "cost_microdollars_per_1k_tokens": (
                    self.settings.cost_microdollars_per_1k_tokens
                ),
            },
        )

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"openai-text:model={self.settings.model_name}:"
            f"dim={self.settings.dimension}:norm={norm}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"
