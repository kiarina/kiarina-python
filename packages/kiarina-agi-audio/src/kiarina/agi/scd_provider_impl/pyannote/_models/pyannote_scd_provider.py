from itertools import combinations
from pathlib import Path
from typing import cast

import numpy as np

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.scd_provider import (
    BaseSCDProvider,
    SCDResult,
    SpeakerProbabilities,
)
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import PyannoteSCDProviderSettings

try:
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime is required to use PyannoteSCDProvider. "
        "Install it with: pip install 'kiarina-agi-audio[scd-provider-pyannote]'"
    ) from exc


class PyannoteSCDProvider(BaseSCDProvider):
    def __init__(self, settings: PyannoteSCDProviderSettings) -> None:
        super().__init__()

        self.settings: PyannoteSCDProviderSettings = settings
        self._session: ort.InferenceSession | None = None
        self._model_path: Path | None = None
        self._powerset_mapping: np.ndarray | None = None

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
                    / "pyannote-segmentation-3.0"
                    / self.settings.model_filename,
                )

        return self._model_path

    @property
    def session(self) -> ort.InferenceSession:
        if self._session is None:
            self._session = ort.InferenceSession(str(self._resolve_model_path()))

        return self._session

    @property
    def powerset_mapping(self) -> np.ndarray:
        if self._powerset_mapping is None:
            self._powerset_mapping = self._build_powerset_mapping(
                self.settings.num_speakers,
                self.settings.max_speakers_per_frame,
            )

        return self._powerset_mapping

    async def _predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult:
        samples = np.asarray(samples, dtype=np.float32)
        samples = self._resample(samples, sample_rate, self.settings.sample_rate)

        if len(samples) == 0:
            return SCDResult(
                speaker_probabilities=np.zeros(
                    (0, self.settings.num_speakers), dtype=np.float32
                ),
                frame_ms=self.settings.window_duration * 1000,
            )

        window_samples = self._window_samples()
        chunks = self._split_chunks(samples, window_samples)
        chunk_probabilities = [self._predict_chunk(chunk) for chunk in chunks]
        speaker_probabilities = np.concatenate(chunk_probabilities, axis=0)
        frame_ms = (
            self.settings.window_duration * 1000 / chunk_probabilities[0].shape[0]
        )

        expected_frames = max(
            1, round(len(samples) * 1000 / self.settings.sample_rate / frame_ms)
        )
        speaker_probabilities = speaker_probabilities[:expected_frames]

        return SCDResult(
            speaker_probabilities=speaker_probabilities.astype(np.float32),
            frame_ms=frame_ms,
        )

    def _predict_chunk(self, samples: MonoSamples) -> SpeakerProbabilities:
        input_name = self._get_input_name()

        inputs = {
            input_name: self._prepare_input(samples, input_name),
        }

        input_names = {input_.name for input_ in self.session.get_inputs()}

        if "sample_rate" in input_names:
            inputs["sample_rate"] = np.array(self.settings.sample_rate, dtype=np.int64)

        if "sr" in input_names:
            inputs["sr"] = np.array(self.settings.sample_rate, dtype=np.int64)

        output_names = (
            [self.settings.output_name] if self.settings.output_name else None
        )

        outputs = self.session.run(output_names, inputs)
        output = np.asarray(outputs[0], dtype=np.float32)
        output = self._normalize_output_shape(output)
        return self._to_speaker_probabilities(output)

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

    def _normalize_output_shape(self, output: np.ndarray) -> np.ndarray:
        output = np.squeeze(output)

        if output.ndim != 2:
            raise ValueError(
                "PyannoteSCDProvider expects 2D model output after squeeze, "
                f"got shape {output.shape}."
            )

        candidate_classes = {
            self.settings.num_speakers,
            self.powerset_mapping.shape[0],
        }

        if (
            output.shape[0] in candidate_classes
            and output.shape[1] not in candidate_classes
        ):
            output = output.T

        return output

    def _to_speaker_probabilities(self, output: np.ndarray) -> SpeakerProbabilities:
        output_kind = self.settings.output_kind

        if output_kind == "auto":
            if output.shape[1] == self.settings.num_speakers:
                output_kind = "multilabel"
            elif output.shape[1] == self.powerset_mapping.shape[0]:
                output_kind = "powerset_log_probs"
            else:
                raise ValueError(
                    "Cannot infer pyannote output kind from shape "
                    f"{output.shape}. Set output_kind explicitly."
                )

        if output_kind == "multilabel":
            return output

        if output.shape[1] != self.powerset_mapping.shape[0]:
            raise ValueError(
                f"{output_kind} expects {self.powerset_mapping.shape[0]} powerset "
                f"classes, got shape {output.shape}."
            )

        if output_kind == "powerset_log_probs":
            powerset_probs = np.exp(output)
        elif output_kind == "powerset_probs":
            powerset_probs = output
        elif output_kind == "powerset_logits":
            powerset_probs = self._softmax(output, axis=1)
        else:
            raise ValueError(f"Unsupported pyannote output_kind: {output_kind}")

        return np.asarray(powerset_probs @ self.powerset_mapping, dtype=np.float32)

    def _get_input_name(self) -> str:
        if self.settings.input_name:
            return self.settings.input_name

        input_names = {input_.name for input_ in self.session.get_inputs()}

        for name in ("waveform", "waveforms", "input", "audio", "x"):
            if name in input_names:
                return name

        return str(self.session.get_inputs()[0].name)

    def _window_samples(self) -> int:
        return round(self.settings.window_duration * self.settings.sample_rate)

    def _split_chunks(
        self, samples: MonoSamples, window_samples: int
    ) -> list[MonoSamples]:
        chunks: list[MonoSamples] = []

        for start in range(0, len(samples), window_samples):
            chunk = samples[start : start + window_samples]

            if len(chunk) < window_samples:
                chunk = np.pad(chunk, (0, window_samples - len(chunk)))

            chunks.append(chunk)

        return chunks

    def _build_powerset_mapping(
        self, num_speakers: int, max_speakers_per_frame: int
    ) -> np.ndarray:
        rows: list[list[float]] = []

        for set_size in range(0, max_speakers_per_frame + 1):
            for current_set in combinations(range(num_speakers), set_size):
                row = [0.0] * num_speakers

                for speaker_index in current_set:
                    row[speaker_index] = 1.0

                rows.append(row)

        return np.asarray(rows, dtype=np.float32)

    def _resample(
        self, samples: MonoSamples, source_sample_rate: int, target_sample_rate: int
    ) -> MonoSamples:
        if source_sample_rate == target_sample_rate:
            return samples

        source_duration = len(samples) / source_sample_rate
        target_length = max(1, round(source_duration * target_sample_rate))
        source_positions = np.linspace(0.0, len(samples) - 1, num=len(samples))
        target_positions = np.linspace(0.0, len(samples) - 1, num=target_length)
        return cast(
            MonoSamples,
            np.interp(target_positions, source_positions, samples).astype(np.float32),
        )

    def _softmax(self, values: np.ndarray, axis: int) -> np.ndarray:
        shifted = values - np.max(values, axis=axis, keepdims=True)
        exp_values = np.exp(shifted)
        return np.asarray(
            exp_values / np.sum(exp_values, axis=axis, keepdims=True),
            dtype=np.float32,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"
