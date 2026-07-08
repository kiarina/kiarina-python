from typing import Protocol, runtime_checkable

from kiarina.agi.audio_types import MonoSamples

from .._schemas.scd_result import SCDResult
from .scd_provider_name import SCDProviderName


@runtime_checkable
class SCDProvider(Protocol):
    name: SCDProviderName

    async def predict(self, samples: MonoSamples, sample_rate: int) -> SCDResult: ...
