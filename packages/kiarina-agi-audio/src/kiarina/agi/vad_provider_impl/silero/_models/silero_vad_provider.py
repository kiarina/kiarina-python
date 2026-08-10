from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.vad_provider import BaseVADProvider, SpeechProbability
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import SileroVADProviderSettings

_SUPPORTED_SAMPLE_RATES = (8000, 16000)

try:
    import onnxruntime as ort  # type: ignore
except ImportError as exc:
    raise ImportError(
        "onnxruntime is required to use SileroVADProvider. "
        "Install it with: pip install 'kiarina-agi-audio[vad-provider-silero]'"
    ) from exc


class SileroVADProvider(BaseVADProvider):
    def __init__(self, settings: SileroVADProviderSettings) -> None:
        super().__init__()

        self.settings: SileroVADProviderSettings = settings
        self._session: ort.InferenceSession | None = None
        self._model_path: Path | None = None
        self._state: np.ndarray | None = None
        self._context: np.ndarray | None = None
        self._last_sample_rate: int | None = None

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
                    / "silero-vad"
                    / self.settings.model_filename,
                )

        return self._model_path

    @property
    def session(self) -> ort.InferenceSession:
        if self._session is None:
            self._session = ort.InferenceSession(str(self._resolve_model_path()))

        return self._session

    async def _predict(
        self, samples: MonoSamples, sample_rate: int
    ) -> SpeechProbability:
        if sample_rate not in _SUPPORTED_SAMPLE_RATES:
            raise ValueError(
                f"SileroVADProvider supports sample rates {_SUPPORTED_SAMPLE_RATES}, "
                f"got {sample_rate}."
            )

        samples = np.asarray(samples, dtype=np.float32)
        samples = self._prepare_samples(samples, sample_rate)
        session_inputs = self.session.get_inputs()
        input_names = {input_.name for input_ in session_inputs}

        audio_input = self._get_audio_input_name(input_names)
        inputs = {audio_input: samples}

        if "state" in input_names:
            inputs["state"] = self._get_state(batch_size=samples.shape[0])

        if "sr" in input_names:
            inputs["sr"] = np.array(sample_rate, dtype=np.int64)

        outputs = self.session.run(None, inputs)
        self._update_state(outputs)
        self._update_context(samples, sample_rate)
        return float(np.asarray(outputs[0]).reshape(-1)[0])

    def _prepare_samples(self, samples: MonoSamples, sample_rate: int) -> np.ndarray:
        samples = samples.reshape(1, -1)

        if self._last_sample_rate != sample_rate:
            self._reset_state()

        context_size = self._get_context_size(sample_rate)

        if self._context is None or self._context.shape[0] != samples.shape[0]:
            self._context = np.zeros((samples.shape[0], context_size), dtype=np.float32)

        self._last_sample_rate = sample_rate
        return np.concatenate([self._context, samples], axis=1).astype(np.float32)

    def _get_audio_input_name(self, input_names: set[str]) -> str:
        for name in ("input", "audio", "x"):
            if name in input_names:
                return name

        return str(self.session.get_inputs()[0].name)

    def _get_state(self, batch_size: int) -> np.ndarray:
        if self._state is None:
            state_shape = self._get_state_shape(batch_size)
            self._state = np.zeros(state_shape, dtype=np.float32)

        return self._state

    def _get_state_shape(self, batch_size: int) -> tuple[int, ...]:
        for input_ in self.session.get_inputs():
            if input_.name != "state":
                continue

            return tuple(
                batch_size
                if dim in (None, "batch", "batch_size")
                else self._to_int_dim(dim)
                for dim in input_.shape
            )

        return (2, batch_size, 128)

    def _update_state(self, outputs: Sequence[Any]) -> None:
        output_names = [output.name for output in self.session.get_outputs()]

        for index, name in enumerate(output_names):
            if name.lower().startswith("state"):
                self._state = np.asarray(outputs[index], dtype=np.float32)
                return

        if len(outputs) > 1:
            self._state = np.asarray(outputs[1], dtype=np.float32)

    def _update_context(self, samples: np.ndarray, sample_rate: int) -> None:
        context_size = self._get_context_size(sample_rate)
        self._context = samples[:, -context_size:].astype(np.float32)

    def _get_context_size(self, sample_rate: int) -> int:
        if sample_rate == 16000:
            return 64

        if sample_rate == 8000:
            return 32

        return max(1, sample_rate // 250)

    def _reset_state(self) -> None:
        self._state = None
        self._context = None

    def _to_int_dim(self, dim: Any) -> int:
        try:
            return int(dim)
        except (TypeError, ValueError):
            return 1
