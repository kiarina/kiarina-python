import csv
from pathlib import Path
from threading import Lock
from typing import Any, cast

import numpy as np

from kiarina.agi.audio_tagging_provider import (
    AudioTagPrediction,
    BaseAudioTaggingProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.common import download_file

from .._settings import YamnetAudioTaggingProviderSettings

try:
    from ai_edge_litert.interpreter import Interpreter  # type: ignore
except ImportError as exc:
    raise ImportError(
        "ai-edge-litert is required to use YamnetAudioTaggingProvider. "
        "Install it with: pip install 'kiarina-agi-audio[audio-tagging-provider-yamnet]'"
    ) from exc


class YamnetAudioTaggingProvider(BaseAudioTaggingProvider):
    def __init__(self, settings: YamnetAudioTaggingProviderSettings) -> None:
        super().__init__()

        self.settings: YamnetAudioTaggingProviderSettings = settings
        self._interpreter: Interpreter | None = None
        self._scores_output_index: int | None = None
        self._input_index: int | None = None
        self._model_path: Path | None = None
        self._class_map_path: Path | None = None
        self._labels: list[str] | None = None
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
                    / "yamnet"
                    / self.settings.model_filename,
                )

        return self._model_path

    def _resolve_class_map_path(self) -> Path:
        if self._class_map_path is None:
            if self.settings.class_map_path is not None:
                self._class_map_path = Path(self.settings.class_map_path).expanduser()
            else:
                self._class_map_path = download_file(
                    self.settings.class_map_url,
                    self.settings.class_map_sha256,
                    user_directory.get_user_cache_dir()
                    / "models"
                    / "yamnet"
                    / self.settings.class_map_filename,
                )

        return self._class_map_path

    @property
    def interpreter(self) -> Interpreter:
        if self._interpreter is None:
            kwargs: dict[str, Any] = {"model_path": str(self._resolve_model_path())}

            if self.settings.num_threads is not None:
                kwargs["num_threads"] = self.settings.num_threads

            self._interpreter = Interpreter(**kwargs)
            self._interpreter.allocate_tensors()

        return self._interpreter

    @property
    def labels(self) -> list[str]:
        if self._labels is None:
            self._labels = _load_class_map(self._resolve_class_map_path())

        return self._labels

    async def _predict(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]:
        target_sample_rate = self.settings.sample_rate

        if sample_rate != target_sample_rate:
            samples = _resample(samples, sample_rate, target_sample_rate)

        samples = np.asarray(samples, dtype=np.float32)

        scores = self._invoke(samples)
        clip_scores = _aggregate(scores, self.settings.aggregation)

        labels = self.labels

        if len(clip_scores) != len(labels):
            raise ValueError(
                "YAMNet output dimension does not match class map: "
                f"scores={len(clip_scores)}, labels={len(labels)}."
            )

        return [
            AudioTagPrediction(label=label, score=float(score))
            for label, score in zip(labels, clip_scores, strict=True)
        ]

    def _invoke(self, samples: MonoSamples) -> np.ndarray:
        with self._lock:
            interpreter = self.interpreter
            input_details = interpreter.get_input_details()
            input_detail = input_details[0]
            input_index = input_detail["index"]
            expected_shape = tuple(input_detail["shape"])

            if expected_shape != (len(samples),):
                interpreter.resize_tensor_input(
                    input_index, [len(samples)], strict=False
                )
                interpreter.allocate_tensors()

            interpreter.set_tensor(input_index, samples)
            interpreter.invoke()

            scores_index = self._resolve_scores_output_index(interpreter)
            scores = interpreter.get_tensor(scores_index)

        return np.asarray(scores, dtype=np.float32)

    def _resolve_scores_output_index(self, interpreter: Interpreter) -> int:
        if self._scores_output_index is not None:
            return self._scores_output_index

        for detail in interpreter.get_output_details():
            shape = tuple(detail["shape"])

            if len(shape) == 2 and shape[-1] == 521:
                self._scores_output_index = int(detail["index"])
                return self._scores_output_index

        raise ValueError(  # pragma: no cover
            "Could not locate YAMNet scores output (expected shape [*, 521])."
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_path})"


def _load_class_map(path: Path) -> list[str]:
    labels: list[str] = []

    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None or "display_name" not in reader.fieldnames:
            raise ValueError(
                f"YAMNet class map must contain a 'display_name' column: {path}"
            )

        for row in reader:
            labels.append(row["display_name"])

    return labels


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


def _aggregate(scores: np.ndarray, mode: str) -> np.ndarray:
    if scores.ndim == 1:
        return scores

    if mode == "max":
        return scores.max(axis=0)

    return scores.mean(axis=0)
