import hashlib
import json
from pathlib import Path
from typing import Any, Literal, cast

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

from .._settings import ClapOnnxAudioEmbeddingProviderSettings

try:
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime is required to use ClapOnnxAudioEmbeddingProvider. "
        "Install it with: pip install 'kiarina-agi-audio[audio-embedding-provider-clap-onnx]'"
    ) from exc


class ClapOnnxAudioEmbeddingProvider(BaseAudioEmbeddingProvider):
    def __init__(self, settings: ClapOnnxAudioEmbeddingProviderSettings) -> None:
        super().__init__()

        self.settings: ClapOnnxAudioEmbeddingProviderSettings = settings
        self.normalize_embedding = settings.normalize_embedding
        self._session: ort.InferenceSession | None = None
        self._model_sha256: str | None = None
        self._model_path: Path | None = None
        self._preprocessor_config_path: Path | None = None
        self._preprocessor_config: dict[str, Any] | None = None
        self._mel_filters: np.ndarray | None = None

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
                    / "clap-onnx"
                    / self.settings.model_filename,
                )

        return self._model_path

    def _resolve_preprocessor_config_path(self) -> Path:
        if self._preprocessor_config_path is None:
            if self.settings.preprocessor_config_path is not None:
                self._preprocessor_config_path = Path(
                    self.settings.preprocessor_config_path
                ).expanduser()
            else:
                self._preprocessor_config_path = download_file(
                    self.settings.preprocessor_config_url,
                    self.settings.preprocessor_config_sha256,
                    user_directory.get_user_cache_dir()
                    / "models"
                    / "clap-onnx"
                    / self.settings.preprocessor_config_filename,
                )

        return self._preprocessor_config_path

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

    @property
    def preprocessor_config(self) -> dict[str, Any]:
        if self._preprocessor_config is None:
            config = {
                "sampling_rate": self.settings.sample_rate,
                "feature_size": self.settings.feature_size,
                "fft_window_size": self.settings.fft_window_size,
                "hop_length": self.settings.hop_length,
                "frequency_min": self.settings.frequency_min,
                "frequency_max": self.settings.frequency_max,
                "max_length_s": self.settings.max_length_s,
                "padding": self.settings.padding,
                "truncation": self.settings.truncation,
            }

            config_path = self._resolve_preprocessor_config_path()
            file_config = json.loads(config_path.read_text(encoding="utf-8"))
            config.update(file_config)

            config.update(self.settings.extra_preprocessor_config)
            config["padding"] = self.settings.padding
            config["truncation"] = self.settings.truncation
            self._preprocessor_config = config

        return self._preprocessor_config

    @property
    def mel_filters(self) -> np.ndarray:
        if self._mel_filters is None:
            config = self.preprocessor_config
            self._mel_filters = _mel_filter_bank(
                num_frequency_bins=int(config["fft_window_size"]) // 2 + 1,
                num_mel_filters=int(config["feature_size"]),
                min_frequency=float(config["frequency_min"]),
                max_frequency=float(config["frequency_max"]),
                sampling_rate=int(config["sampling_rate"]),
            )

        return self._mel_filters

    def get_space(self) -> EmbeddingSpace:
        return EmbeddingSpace(
            kind="sound",
            space_id=self._embedding_space_id(),
            dimension=self.settings.dimension,
            metadata={
                "preprocessor": "clap-log-mel-numpy",
            },
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
        target_sample_rate = int(self.preprocessor_config["sampling_rate"])
        samples = _resample(samples, sample_rate, target_sample_rate)
        input_name = self._get_input_name()
        input_features, is_longer = self._prepare_audio_inputs(samples, input_name)
        inputs = {input_name: input_features}
        input_names = {input_.name for input_ in self.session.get_inputs()}

        if "is_longer" in input_names:
            inputs["is_longer"] = is_longer

        if "sample_rate" in input_names:
            inputs["sample_rate"] = np.array(target_sample_rate, dtype=np.int64)

        if "sr" in input_names:
            inputs["sr"] = np.array(target_sample_rate, dtype=np.int64)

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
                "sample_rate": target_sample_rate,
                "samples": len(samples),
                "preprocessor": "clap-log-mel-numpy",
                "model_output_normalized": True,
            },
        )

    def _get_input_name(self) -> str:
        if self.settings.input_name:
            return self.settings.input_name

        input_names = {input_.name for input_ in self.session.get_inputs()}

        for name in ("audio", "input_features", "input", "waveform", "x"):
            if name in input_names:
                return name

        return str(self.session.get_inputs()[0].name)

    def _prepare_audio_inputs(
        self, samples: MonoSamples, input_name: str
    ) -> tuple[np.ndarray, np.ndarray]:
        input_info = next(
            input_ for input_ in self.session.get_inputs() if input_.name == input_name
        )
        rank = len(input_info.shape)

        if input_name == "input_features" or rank == 4:
            return self._extract_input_features(samples)

        is_longer = np.array([[False]], dtype=bool)

        if rank == 3:
            return samples.reshape(1, 1, -1).astype(np.float32), is_longer

        if rank == 2:
            return samples.reshape(1, -1).astype(np.float32), is_longer

        return samples.astype(np.float32), is_longer

    def _extract_input_features(
        self, samples: MonoSamples
    ) -> tuple[np.ndarray, np.ndarray]:
        config = self.preprocessor_config
        sample_rate = int(config["sampling_rate"])
        max_samples = int(
            config.get("nb_max_samples") or int(config["max_length_s"]) * sample_rate
        )
        hop_length = int(config["hop_length"])
        fft_window_size = int(config["fft_window_size"])
        padding = str(config["padding"])
        truncation = str(config["truncation"])

        samples, longer = _fit_waveform(
            samples,
            max_samples=max_samples,
            padding=padding,
            truncation=truncation,
        )
        mel = _log_mel_spectrogram(
            samples,
            fft_window_size=fft_window_size,
            hop_length=hop_length,
            mel_filters=self.mel_filters,
        )

        expected_frames = max_samples // hop_length + 1
        mel = _fit_frames(mel, expected_frames)
        input_features = mel.reshape(1, 1, mel.shape[0], mel.shape[1]).astype(
            np.float32
        )
        is_longer = np.array([[longer]], dtype=bool)
        return input_features, is_longer

    def _embedding_space_id(self) -> str:
        norm = "l2" if self.normalize_embedding else "model-l2"
        return (
            f"clap-onnx:sha256={self.model_sha256}:"
            f"sr={self.preprocessor_config['sampling_rate']}:"
            f"pre=logmel-v1:dim={self.settings.dimension}:norm={norm}"
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


def _fit_waveform(
    samples: MonoSamples,
    *,
    max_samples: int,
    padding: str,
    truncation: str,
) -> tuple[MonoSamples, bool]:
    if len(samples) == 0:
        return np.zeros(max_samples, dtype=np.float32), False

    if len(samples) > max_samples:
        start = (len(samples) - max_samples) // 2 if truncation == "center" else 0
        return samples[start : start + max_samples].astype(np.float32), True

    if len(samples) == max_samples:
        return samples.astype(np.float32), False

    if padding in ("repeat", "repeatpad"):
        repeat_count = max_samples // len(samples)
        repeats = repeat_count if padding == "repeatpad" else repeat_count + 1
        samples = np.tile(samples, repeats)

    clipped = samples[:max_samples]
    return np.pad(
        clipped,
        (0, max_samples - len(clipped)),
        mode="constant",
        constant_values=0.0,
    ).astype(np.float32), False


def _log_mel_spectrogram(
    samples: MonoSamples,
    *,
    fft_window_size: int,
    hop_length: int,
    mel_filters: np.ndarray,
) -> np.ndarray:
    pad = fft_window_size // 2
    pad_mode: Literal["reflect", "constant"] = (
        "reflect" if len(samples) > 1 else "constant"
    )
    samples = np.pad(samples, (pad, pad), mode=pad_mode)
    window = np.hanning(fft_window_size + 1)[:-1].astype(np.float32)
    num_frames = 1 + (len(samples) - fft_window_size) // hop_length
    frames = np.lib.stride_tricks.sliding_window_view(samples, fft_window_size)[
        ::hop_length
    ][:num_frames]
    spectrum = np.fft.rfft(frames * window, n=fft_window_size)
    power = np.abs(spectrum) ** 2
    mel = np.asarray(np.maximum(power @ mel_filters, 1e-10), dtype=np.float32)
    return (10.0 * np.log10(mel)).astype(np.float32)


def _fit_frames(mel: np.ndarray, expected_frames: int) -> np.ndarray:
    if mel.shape[0] == expected_frames:
        return mel.astype(np.float32)

    if mel.shape[0] > expected_frames:
        return mel[:expected_frames].astype(np.float32)

    return np.pad(
        mel,
        ((0, expected_frames - mel.shape[0]), (0, 0)),
        mode="constant",
        constant_values=0.0,
    ).astype(np.float32)


def _mel_filter_bank(
    *,
    num_frequency_bins: int,
    num_mel_filters: int,
    min_frequency: float,
    max_frequency: float,
    sampling_rate: int,
) -> np.ndarray:
    min_mel = _hz_to_mel_htk(min_frequency)
    max_mel = _hz_to_mel_htk(max_frequency)
    mel_points = np.linspace(min_mel, max_mel, num_mel_filters + 2)
    hz_points = _mel_to_hz_htk(mel_points)
    fft_freqs = np.linspace(0.0, sampling_rate / 2, num_frequency_bins)
    filters = np.zeros((num_frequency_bins, num_mel_filters), dtype=np.float32)

    for index in range(num_mel_filters):
        lower = hz_points[index]
        center = hz_points[index + 1]
        upper = hz_points[index + 2]

        up_slope = (fft_freqs - lower) / max(center - lower, 1e-12)
        down_slope = (upper - fft_freqs) / max(upper - center, 1e-12)
        filters[:, index] = np.maximum(0.0, np.minimum(up_slope, down_slope))

    return filters


def _hz_to_mel_htk(frequency: float) -> float:
    return float(2595.0 * np.log10(1.0 + frequency / 700.0))


def _mel_to_hz_htk(mel: np.ndarray) -> np.ndarray:
    return np.asarray(700.0 * (10.0 ** (mel / 2595.0) - 1.0), dtype=np.float32)
