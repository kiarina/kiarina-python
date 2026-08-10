from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._types.image_embedding_provider import ImageEmbeddingProvider
from .._types.image_embedding_provider_name import ImageEmbeddingProviderName


class BaseImageEmbeddingProvider(ImageEmbeddingProvider, ABC):
    def __init__(self) -> None:
        self._name: ImageEmbeddingProviderName | None = None

    @property
    def name(self) -> ImageEmbeddingProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("ImageEmbeddingProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: ImageEmbeddingProviderName) -> None:
        self._name = value

    async def embed(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        pixels = _validate_pixels(pixels)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(image_embedding_provider=f"{self}")

        space = self.get_space()

        embedding = await self._embed(
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        if embedding.kind != space.kind:
            raise ValueError(
                f"Embedding kind mismatch: {embedding.kind!r} != {space.kind!r}."
            )

        if embedding.space_id != space.space_id:
            raise ValueError(
                "Embedding space_id mismatch: "
                f"{embedding.space_id!r} != {space.space_id!r}."
            )

        if len(embedding.vector) != space.dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"{len(embedding.vector)} != {space.dimension}."
            )

        return embedding

    @abstractmethod
    def get_space(self) -> EmbeddingSpace: ...

    @abstractmethod
    async def _embed(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding: ...

    # Shared pre/post-processing utilities for subclasses.

    @staticmethod
    def _to_bgr(pixels: ImagePixels) -> ImagePixels:
        return np.ascontiguousarray(pixels[..., ::-1])

    def __str__(self) -> str:
        return self.__class__.__name__


def _validate_pixels(pixels: ImagePixels) -> ImagePixels:
    pixels = np.asarray(pixels)

    if pixels.ndim != 3 or pixels.shape[2] != 3:
        raise ValueError(
            "ImageEmbeddingProvider expects pixels shaped as [H, W, 3] (RGB), "
            f"got shape {pixels.shape}."
        )

    if pixels.dtype != np.uint8:
        raise ValueError(
            f"ImageEmbeddingProvider expects uint8 pixels, got dtype {pixels.dtype}."
        )

    return pixels
