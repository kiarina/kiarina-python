import numpy as np

from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.audio_consumer_impl.ambient import AmbientAudioEvent
from kiarina.agi.audio_consumer_impl.stt import STTAudioEvent
from kiarina.agi.audio_event_bundler_impl.ambient import (
    AmbientAudioEventBundler,
    create_ambient_audio_event_bundler,
)
from kiarina.agi.audio_tagging_provider import AudioTagPrediction
from kiarina.agi.embedding import Embedding
from kiarina.agi.file_bundle import FileBundle, FileBundleTextContent
from kiarina.agi.speaker_change_detector import Speech


def _embedding(vector: list[float]) -> Embedding:
    return Embedding.from_numpy(
        kind="sound",
        space_id="test",
        vector=np.asarray(vector, dtype=np.float32),
        metadata={},
    )


def _ambient_event(
    *,
    start: float,
    end: float,
    vector: list[float],
    predictions: list[AudioTagPrediction] | None = None,
) -> AmbientAudioEvent:
    return AmbientAudioEvent(
        consumer_name="ambient",
        start_timestamp=start,
        end_timestamp=end,
        predictions=predictions or [],
        embedding=_embedding(vector),
    )


def test_create_returns_ambient_bundler_with_default_threshold() -> None:
    bundler = create_ambient_audio_event_bundler()

    assert isinstance(bundler, AmbientAudioEventBundler)
    assert bundler.settings.change_similarity_threshold == 0.55


def test_create_accepts_kwargs_override() -> None:
    bundler = create_ambient_audio_event_bundler(change_similarity_threshold=0.9)

    assert bundler.settings.change_similarity_threshold == 0.9


def test_bundle_returns_none_for_empty_events() -> None:
    bundler = create_ambient_audio_event_bundler()
    assert bundler.bundle([]) is None


def test_bundle_ignores_non_ambient_events() -> None:
    bundler = create_ambient_audio_event_bundler()

    stt_event = STTAudioEvent(
        consumer_name="stt",
        speech=Speech(
            samples=np.zeros(1, dtype=np.float32),
            sample_rate=16000,
            start_timestamp=0.0,
            end_timestamp=1.0,
            speaker_index=0,
        ),
        text="hello",
        embedding=None,
    )

    assert bundler.bundle([stt_event]) is None


def test_bundle_emits_predictions_and_similarity_change() -> None:
    bundler = create_ambient_audio_event_bundler(change_similarity_threshold=0.5)

    events: list[AudioEvent] = [
        _ambient_event(
            start=0.0,
            end=1.0,
            vector=[1.0, 0.0],
            predictions=[
                AudioTagPrediction("Music", 0.82),
                AudioTagPrediction("Speech", 0.31),
                AudioTagPrediction("Inside, small room", 0.22),
            ],
        ),
        _ambient_event(
            start=1.0,
            end=2.0,
            vector=[1.0, 0.0],  # identical → similarity=1.0, no change
            predictions=[AudioTagPrediction("Music", 0.80)],
        ),
        _ambient_event(
            start=2.0,
            end=3.0,
            vector=[0.0, 1.0],  # orthogonal → similarity=0.0, change
            predictions=[AudioTagPrediction("Silence", 0.10)],
        ),
    ]

    bundle = bundler.bundle(events)

    assert isinstance(bundle, FileBundle)
    assert len(bundle.manifest.contents) == 1
    content = bundle.manifest.contents[0]
    assert isinstance(content, FileBundleTextContent)
    assert content.visibility == "always"

    ambient_text = content.text
    assert ambient_text.startswith("<ambient>")
    assert ambient_text.endswith("</ambient>")
    assert "[Music] 0.820" in ambient_text
    assert "[Inside, small room] 0.220" in ambient_text
    # First event has no previous; second event has similarity=1.000, no change.
    assert '<similarity previous="1.000" />' in ambient_text
    # Third event has similarity=0.000 (< 0.5) → change tag emitted.
    assert '<change similarity="0.000">ambience changed</change>' in ambient_text


def test_bundle_above_threshold_emits_similarity_without_change() -> None:
    bundler = create_ambient_audio_event_bundler(change_similarity_threshold=0.5)

    events: list[AudioEvent] = [
        _ambient_event(start=0.0, end=1.0, vector=[1.0, 0.0]),
        _ambient_event(start=1.0, end=2.0, vector=[1.0, 0.0]),
    ]

    bundle = bundler.bundle(events)
    assert bundle is not None
    ambient_text = bundle.manifest.contents[0].text  # type: ignore[union-attr]

    assert '<similarity previous="1.000" />' in ambient_text
    assert "<change " not in ambient_text


def test_bundle_escapes_html_in_tag_labels() -> None:
    bundler = create_ambient_audio_event_bundler()

    events: list[AudioEvent] = [
        _ambient_event(
            start=0.0,
            end=1.0,
            vector=[1.0, 0.0],
            predictions=[AudioTagPrediction("Bell & whistle <x>", 0.5)],
        ),
    ]

    bundle = bundler.bundle(events)
    assert bundle is not None
    ambient_text = bundle.manifest.contents[0].text  # type: ignore[union-attr]

    assert "Bell &amp; whistle &lt;x&gt;" in ambient_text
    assert "<x>" not in ambient_text.replace("&lt;x&gt;", "")
