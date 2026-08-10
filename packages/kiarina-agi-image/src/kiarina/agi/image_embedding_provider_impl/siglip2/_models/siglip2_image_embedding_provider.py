import asyncio
import hashlib
from pathlib import Path

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.image_embedding_provider import (
    BaseImageEmbeddingProvider,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import SigLIP2ImageEmbeddingProviderSettings

try:
    import cv2
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime and opencv-python are required to use "
        "SigLIP2ImageEmbeddingProvider. "
        "Install them with: pip install 'kiarina-agi-image[image-embedding-provider-siglip2]'"
    ) from exc


class SigLIP2ImageEmbeddingProvider(BaseImageEmbeddingProvider):
    def __init__(self, settings: SigLIP2ImageEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: SigLIP2ImageEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._session: ort.InferenceSession | None = None
        self._model_path: Path | None = None
        self._model_sha256: str | None = None

    def _resolve_model_path(self) -> Path:
        if self._model_path is None:
            if self.settings.model_path is not None:
                self._model_path = Path(self.settings.model_path).expanduser()
            else:
                self._model_path = download_file(
                    self.settings.model_url,
                    self.settings.model_sha256,
                    user_directory.get_user_cache_dir()
                    / "models"
                    / "siglip2"
                    / self.settings.model_filename,
                )

        return self._model_path

    @property
    def session(self) -> ort.InferenceSession:
        if self._session is None:
            self._session = ort.InferenceSession(str(self._resolve_model_path()))

        return self._session

    @property
    def model_sha256(self) -> str:
        if self._model_sha256 is None:
            self._model_sha256 = _sha256_file(self._resolve_model_path())

        return self._model_sha256

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
        return await asyncio.to_thread(self._embed_sync, pixels)

    def _embed_sync(self, pixels: ImagePixels) -> Embedding:
        space = self.get_space()

        image = self._preprocess(pixels)
        outputs = self.session.run(self._output_names(), {self._input_name(): image})
        embedding = np.asarray(outputs[0], dtype=np.float32).reshape(-1)

        if self.normalize_embedding:
            embedding = l2_normalize(embedding)

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=embedding,
            metadata={
                "height": int(pixels.shape[0]),
                "width": int(pixels.shape[1]),
            },
        )

    def _preprocess(self, pixels: ImagePixels) -> np.ndarray:
        size = self.settings.input_size
        resized = cv2.resize(pixels, (size, size), interpolation=cv2.INTER_LINEAR)
        image = resized.astype(np.float32) / 255.0
        mean = np.asarray(self.settings.image_mean, dtype=np.float32)
        std = np.asarray(self.settings.image_std, dtype=np.float32)
        image = (image - mean) / std
        image = np.transpose(image, (2, 0, 1))[np.newaxis, ...]
        return np.ascontiguousarray(image, dtype=np.float32)

    def _input_name(self) -> str:
        if self.settings.image_input_name:
            return self.settings.image_input_name

        return str(self.session.get_inputs()[0].name)

    def _output_names(self) -> list[str] | None:
        return [self.settings.output_name] if self.settings.output_name else None

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"siglip2:sha256={self.model_sha256}:"
            f"size={self.settings.input_size}:dim={self.settings.dimension}:norm={norm}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"


def _sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()
