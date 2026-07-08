import pytest

from kiarina.agi.audio_consumer import (
    AudioEvent,
    BaseAudioConsumer,
    audio_consumer_registry,
)
from kiarina.agi.audio_source import AudioChunk
from kiarina.agi.run_context import RunContext


class FakeAudioConsumer(BaseAudioConsumer[AudioEvent]):
    async def accept(self, chunk: AudioChunk) -> list[AudioEvent]:  # pragma: no cover
        return []

    async def flush(self) -> list[AudioEvent]:  # pragma: no cover
        return []


def test_audio_consumer_registry_injects_run_context(run_context: RunContext) -> None:
    audio_consumer_registry.register("test-fake", lambda: FakeAudioConsumer())

    try:
        consumer = audio_consumer_registry.resolve(
            "test-fake",
            run_context=run_context,
        )

        assert isinstance(consumer, FakeAudioConsumer)
        assert consumer.run_context is run_context
    finally:
        audio_consumer_registry.unregister("test-fake")


def test_audio_consumer_registry_requires_run_context() -> None:
    audio_consumer_registry.register("test-fake", lambda: FakeAudioConsumer())

    try:
        with pytest.raises(ValueError, match="run_context"):
            audio_consumer_registry.resolve("test-fake")
    finally:
        audio_consumer_registry.unregister("test-fake")
