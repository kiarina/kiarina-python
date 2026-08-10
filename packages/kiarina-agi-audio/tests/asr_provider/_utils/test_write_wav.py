import io
import wave
from pathlib import Path

import numpy as np

from kiarina.agi.asr_provider import write_wav


def test_write_wav_to_path(tmp_path: Path) -> None:
    file_path = tmp_path / "audio.wav"
    audio = np.asarray([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float32)

    write_wav(file_path, audio, sample_rate=16_000)

    with wave.open(str(file_path), "rb") as audio_file:
        assert audio_file.getnchannels() == 1
        assert audio_file.getsampwidth() == 2
        assert audio_file.getframerate() == 16_000
        frames = audio_file.readframes(audio_file.getnframes())

    samples = np.frombuffer(frames, dtype=np.int16)
    assert samples.tolist() == [-32767, -32767, 0, 32767, 32767]


def test_write_wav_to_binary_io() -> None:
    buffer = io.BytesIO()
    audio = np.asarray([0.0, 0.5, -0.5], dtype=np.float32)

    write_wav(buffer, audio, sample_rate=16_000)
    buffer.seek(0)

    with wave.open(buffer, "rb") as audio_file:
        assert audio_file.getnchannels() == 1
        assert audio_file.getframerate() == 16_000
        frames = audio_file.readframes(audio_file.getnframes())

    samples = np.frombuffer(frames, dtype=np.int16)
    assert samples.tolist() == [0, 16383, -16383]
