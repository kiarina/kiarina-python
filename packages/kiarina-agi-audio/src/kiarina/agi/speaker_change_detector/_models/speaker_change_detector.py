from dataclasses import dataclass

import numpy as np

from kiarina.agi.audio_types import AudioSamples, MonoSamples
from kiarina.agi.scd_model import SCDModel
from kiarina.agi.scd_provider import SpeakerProbabilities

from .._schemas.speech import Speech
from .._settings import SpeakerChangeDetectorSettings

_UNKNOWN_SILENCE = -1
_UNKNOWN_OVERLAP = -2


@dataclass
class _Run:
    label: int
    start_frame: int
    end_frame: int

    @property
    def frame_count(self) -> int:
        return self.end_frame - self.start_frame


class SpeakerChangeDetector:
    def __init__(
        self,
        scd_model: SCDModel,
        settings: SpeakerChangeDetectorSettings,
    ) -> None:
        self.scd_model: SCDModel = scd_model
        self.settings: SpeakerChangeDetectorSettings = settings

    async def detect(
        self,
        samples: AudioSamples,
        sample_rate: int,
        timestamp: float,
    ) -> list[Speech]:
        samples = _to_mono(samples)

        if len(samples) == 0:
            return []

        result = await self.scd_model.predict(samples, sample_rate)
        probabilities = result.speaker_probabilities

        if probabilities.shape[0] == 0:
            return [
                self._create_speech(
                    samples,
                    sample_rate,
                    timestamp,
                    start_sample=0,
                    end_sample=len(samples),
                    speaker_index=_UNKNOWN_SILENCE,
                )
            ]

        labels = self._detect_frame_labels(probabilities)
        labels = self._merge_silence_labels(labels)

        runs = self._labels_to_runs(labels)
        runs = self._smooth_short_runs(
            runs,
            min_frames=self._ms_to_frames(self.settings.min_change_ms, result.frame_ms),
        )
        runs = self._smooth_short_runs(
            runs,
            min_frames=self._ms_to_frames(self.settings.min_speech_ms, result.frame_ms),
        )

        return [
            self._run_to_speech(
                run,
                samples=samples,
                sample_rate=sample_rate,
                timestamp=timestamp,
                frame_ms=result.frame_ms,
                num_frames=len(labels),
            )
            for run in runs
        ]

    def _detect_frame_labels(self, probabilities: SpeakerProbabilities) -> list[int]:
        labels: list[int] = []

        for frame in probabilities:
            if len(frame) == 0:
                labels.append(_UNKNOWN_SILENCE)
                continue

            active_indexes = np.flatnonzero(frame >= self.settings.threshold)

            if len(active_indexes) == 0:
                labels.append(_UNKNOWN_SILENCE)
                continue

            ordered = np.argsort(frame)[::-1]
            top_index = int(ordered[0])

            if len(active_indexes) >= 2:
                second_index = int(ordered[1])
                margin = float(frame[top_index] - frame[second_index])

                if margin <= self.settings.overlap_margin:
                    labels.append(_UNKNOWN_OVERLAP)
                    continue

            labels.append(top_index)

        return labels

    def _merge_silence_labels(self, labels: list[int]) -> list[int]:
        if all(label == _UNKNOWN_SILENCE for label in labels):
            return labels

        merged = labels.copy()
        index = 0

        while index < len(merged):
            if merged[index] != _UNKNOWN_SILENCE:
                index += 1
                continue

            start = index

            while index < len(merged) and merged[index] == _UNKNOWN_SILENCE:
                index += 1

            end = index

            previous_label = merged[start - 1] if start > 0 else None
            next_label = merged[end] if end < len(merged) else None

            if previous_label is None and next_label is None:
                continue

            if previous_label is None:
                fill_point = start
            elif next_label is None or previous_label == next_label:
                fill_point = end
            else:
                fill_point = start + (end - start) // 2

            for fill_index in range(start, end):
                if fill_index < fill_point and previous_label is not None:
                    merged[fill_index] = previous_label
                elif next_label is not None:
                    merged[fill_index] = next_label
                elif previous_label is not None:
                    merged[fill_index] = previous_label

        return merged

    def _labels_to_runs(self, labels: list[int]) -> list[_Run]:
        if not labels:
            return []

        runs: list[_Run] = []
        start_frame = 0
        current_label = labels[0]

        for index, label in enumerate(labels[1:], start=1):
            if label == current_label:
                continue

            runs.append(_Run(current_label, start_frame, index))
            start_frame = index
            current_label = label

        runs.append(_Run(current_label, start_frame, len(labels)))
        return runs

    def _smooth_short_runs(self, runs: list[_Run], *, min_frames: int) -> list[_Run]:
        if min_frames <= 1 or len(runs) <= 1:
            return runs

        labels = [label for run in runs for label in [run.label] * run.frame_count]

        for index, run in enumerate(runs):
            if run.frame_count >= min_frames:
                continue

            previous_run = runs[index - 1] if index > 0 else None
            next_run = runs[index + 1] if index + 1 < len(runs) else None

            if previous_run is not None and next_run is not None:
                if previous_run.label == next_run.label:
                    replacement = previous_run.label
                elif previous_run.frame_count >= next_run.frame_count:
                    replacement = previous_run.label
                else:
                    replacement = next_run.label

            elif previous_run is not None:
                replacement = previous_run.label

            elif next_run is not None:
                replacement = next_run.label

            else:
                replacement = run.label

            for frame_index in range(run.start_frame, run.end_frame):
                labels[frame_index] = replacement

        return self._labels_to_runs(labels)

    def _run_to_speech(
        self,
        run: _Run,
        *,
        samples: MonoSamples,
        sample_rate: int,
        timestamp: float,
        frame_ms: float,
        num_frames: int,
    ) -> Speech:
        start_sample = self._frame_to_sample(run.start_frame, sample_rate, frame_ms)
        end_sample = (
            len(samples)
            if run.end_frame >= num_frames
            else self._frame_to_sample(run.end_frame, sample_rate, frame_ms)
        )

        return self._create_speech(
            samples,
            sample_rate,
            timestamp,
            start_sample=start_sample,
            end_sample=end_sample,
            speaker_index=run.label,
        )

    def _create_speech(
        self,
        samples: MonoSamples,
        sample_rate: int,
        timestamp: float,
        *,
        start_sample: int,
        end_sample: int,
        speaker_index: int,
    ) -> Speech:
        start_sample = max(0, min(start_sample, len(samples)))
        end_sample = max(start_sample, min(end_sample, len(samples)))

        return Speech(
            samples=samples[start_sample:end_sample],
            sample_rate=sample_rate,
            start_timestamp=timestamp + start_sample / sample_rate,
            end_timestamp=timestamp + end_sample / sample_rate,
            speaker_index=speaker_index,
        )

    def _frame_to_sample(
        self, frame_index: int, sample_rate: int, frame_ms: float
    ) -> int:
        return round(frame_index * frame_ms * sample_rate / 1000)

    def _ms_to_frames(self, milliseconds: int, frame_ms: float) -> int:
        return max(1, round(milliseconds / frame_ms))


def _to_mono(samples: AudioSamples) -> MonoSamples:
    samples = np.asarray(samples)

    if samples.ndim == 1:
        return samples

    if samples.ndim == 2:
        return samples[0] if samples.shape[0] == 1 else samples.mean(axis=0)

    raise ValueError(  # pragma: no cover
        f"samples must be 1D or 2D [Channels, Samples], got shape {samples.shape}."
    )
