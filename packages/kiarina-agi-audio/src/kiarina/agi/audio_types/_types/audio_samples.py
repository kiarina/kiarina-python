from typing import TypeAlias

from .mono_samples import MonoSamples
from .multi_channel_samples import MultiChannelSamples

AudioSamples: TypeAlias = MonoSamples | MultiChannelSamples
"""Mono or multi-channel float32 audio samples."""
