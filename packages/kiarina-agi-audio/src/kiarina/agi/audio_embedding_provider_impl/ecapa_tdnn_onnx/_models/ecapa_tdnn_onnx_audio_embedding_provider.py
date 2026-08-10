import hashlib
from pathlib import Path
from typing import cast

import numpy as np

from kiarina.agi.audio_embedding_provider import (
    BaseAudioEmbeddingProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace, l2_normalize
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import EcapaTDNNOnnxAudioEmbeddingProviderSettings

try:
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime is required to use EcapaTDNNOnnxAudioEmbeddingProvider. "
        "Install it with: pip install 'kiarina-agi-audio[audio-embedding-provider-ecapa-tdnn-onnx]'"
    ) from exc


class EcapaTDNNOnnxAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
    def __init__(self, settings: EcapaTDNNOnnxAudioEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: EcapaTDNNOnnxAudioEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._session: ort.InferenceSession | None = None
        self._model_sha256: str | None = None
        self._model_path: Path | None = None

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
                    / "ecapa-tdnn-onnx"
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
            kind="speaker",
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
        )

    async def _embed(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> Embedding:
        space = self.get_space()
        samples = np.asarray(samples, dtype=np.float32)
        samples = _resample(samples, sample_rate, self.settings.sample_rate)
        input_name = self._get_input_name()
        inputs = {input_name: self._prepare_input(samples, input_name)}
        input_names = {input_.name for input_ in self.session.get_inputs()}

        if "sample_rate" in input_names:
            inputs["sample_rate"] = np.array(self.settings.sample_rate, dtype=np.int64)

        if "sr" in input_names:
            inputs["sr"] = np.array(self.settings.sample_rate, dtype=np.int64)

        output_names = (
            [self.settings.output_name] if self.settings.output_name else None
        )
        outputs = self.session.run(output_names, inputs)
        embedding = np.asarray(outputs[0], dtype=np.float32).reshape(-1)

        if self.normalize_embedding:
            embedding = l2_normalize(embedding)

        return Embedding.from_numpy(
            kind=space.kind,
            space_id=space.space_id,
            vector=embedding,
            metadata={
                "source_sample_rate": sample_rate,
                "sample_rate": self.settings.sample_rate,
                "samples": len(samples),
            },
        )

    def _get_input_name(self) -> str:
        if self.settings.input_name:
            return self.settings.input_name

        input_names = {input_.name for input_ in self.session.get_inputs()}

        for name in ("waveform", "waveforms", "input", "audio", "x"):
            if name in input_names:
                return name

        return str(self.session.get_inputs()[0].name)

    def _prepare_input(self, samples: MonoSamples, input_name: str) -> np.ndarray:
        input_info = next(
            input_ for input_ in self.session.get_inputs() if input_.name == input_name
        )
        rank = len(input_info.shape)

        if rank == 3:
            return samples.reshape(1, 1, -1).astype(np.float32)

        if rank == 2:
            return samples.reshape(1, -1).astype(np.float32)

        return samples.astype(np.float32)

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "none"
        return (
            f"ecapa-tdnn-onnx:sha256={self.model_sha256}:"
            f"sr={self.settings.sample_rate}:dim={self.settings.dimension}:norm={norm}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"


def _sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _resample(
    samples: MonoSamples, source_sample_rate: int, target_sample_rate: int
) -> MonoSamples:
    if source_sample_rate == target_sample_rate:
        return samples

    if len(samples) == 0:
        return samples

    source_duration = len(samples) / source_sample_rate
    target_length = max(1, round(source_duration * target_sample_rate))
    source_positions = np.linspace(0.0, len(samples) - 1, num=len(samples))
    target_positions = np.linspace(0.0, len(samples) - 1, num=target_length)
    return cast(
        MonoSamples,
        np.interp(target_positions, source_positions, samples).astype(np.float32),
    )
