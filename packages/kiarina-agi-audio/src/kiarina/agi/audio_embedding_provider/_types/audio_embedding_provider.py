from typing import Protocol, runtime_checkable

from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding, EmbeddingSpace
from kiarina.agi.run_context import RunContext

from .audio_embedding_provider_name import AudioEmbeddingProviderName


@runtime_checkable
class AudioEmbeddingProvider(Protocol):
    name: AudioEmbeddingProviderName

    def get_space(self) -> EmbeddingSpace: ...

    async def embed(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding: ...
