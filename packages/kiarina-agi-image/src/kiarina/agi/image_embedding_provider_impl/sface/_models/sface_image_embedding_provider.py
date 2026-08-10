import asyncio
import hashlib
from pathlib import Path
from threading import Lock

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

from .._settings import SFaceImageEmbeddingProviderSettings

try:
    import cv2
except ImportError as exc:
    raise ImportError(
        "opencv-python is required to use SFaceImageEmbeddingProvider. "
        "Install it with: pip install 'kiarina-agi-image[image-embedding-provider-sface]'"
    ) from exc


class SFaceImageEmbeddingProvider(BaseImageEmbeddingProvider):
    def __init__(self, settings: SFaceImageEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: SFaceImageEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._recognizer: cv2.FaceRecognizerSF | None = None
        self._model_path: Path | None = None
        self._model_sha256: str | None = None
        self._lock = Lock()

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
                    / "sface"
                    / self.settings.model_filename,
                )

        return self._model_path

    @property
    def recognizer(self) -> "cv2.FaceRecognizerSF":
        if self._recognizer is None:
            self._recognizer = cv2.FaceRecognizerSF.create(
                str(self._resolve_model_path()), ""
            )

        return self._recognizer

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

        size = self.settings.input_size
        face = pixels

        if face.shape[0] != size or face.shape[1] != size:
            face = cv2.resize(face, (size, size), interpolation=cv2.INTER_LINEAR)

        image = self._to_bgr(face)

        with self._lock:
            feature = self.recognizer.feature(image)

        embedding = np.asarray(feature, dtype=np.float32).reshape(-1)

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

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"sface:sha256={self.model_sha256}:"
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
