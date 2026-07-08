import wave
from pathlib import Path
from typing import BinaryIO

import numpy as np

from kiarina.agi.audio_types import MonoSamples


def write_wav(
    file: str | Path | BinaryIO,
    samples: MonoSamples,
    sample_rate: int,
) -> None:
    samples = np.asarray(samples)

    if samples.ndim != 1:
        raise ValueError(
            f"audio samples must be 1D mono data, got shape {samples.shape}."
        )

    if samples.dtype.kind == "f":
        samples = np.clip(samples, -1.0, 1.0)
        samples = (samples * np.iinfo(np.int16).max).astype(np.int16)
    else:
        samples = samples.astype(np.int16)

    if isinstance(file, (str, Path)):
        with open(file, "wb") as output_file:
            with wave.open(output_file, "wb") as audio_file:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(sample_rate)
                audio_file.writeframes(samples.tobytes())
        return

    with wave.open(file, "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(sample_rate)
        audio_file.writeframes(samples.tobytes())
