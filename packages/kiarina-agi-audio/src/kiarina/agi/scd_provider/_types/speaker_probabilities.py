from typing import TypeAlias

import numpy as np
from jaxtyping import Float32

SpeakerProbabilities: TypeAlias = Float32[np.ndarray, "frames speakers"]  # noqa: F722
"""
shape:  (num_frames, num_speakers)
dtype:  float32
range:  [0.0, 1.0]
axis=0: time, where the first frame starts at the beginning of the audio
axis=1: speaker channel
"""
