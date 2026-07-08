import io
import wave

import numpy as np

from kiarina.agi.asr_provider import encode_wav


def test_encode_wav() -> None:
    data = encode_wav(np.asarray([0.0, 0.5, -0.5], dtype=np.float32), sample_rate=8000)

    with wave.open(io.BytesIO(data), "rb") as audio_file:
        assert audio_file.getnchannels() == 1
        assert audio_file.getframerate() == 8000
