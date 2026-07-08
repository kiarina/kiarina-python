import io

from kiarina.agi.audio_types import MonoSamples

from .write_wav import write_wav


def encode_wav(audio: MonoSamples, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    write_wav(buffer, audio, sample_rate)
    return buffer.getvalue()
