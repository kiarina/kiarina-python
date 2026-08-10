import re

import numpy as np

from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.audio_consumer_impl.ambient import AmbientAudioEvent
from kiarina.agi.audio_consumer_impl.stt import STTAudioEvent
from kiarina.agi.audio_event_bundler_impl.ambient import (
    create_ambient_audio_event_bundler,
)
from kiarina.agi.audio_event_bundler_impl.stt import (
    STTAudioEventBundler,
    create_stt_audio_event_bundler,
)
from kiarina.agi.embedding import Embedding
from kiarina.agi.file_bundle import FileBundle, FileBundleTextContent
from kiarina.agi.speaker_change_detector import Speech


def _make_speech(start: float, end: float, speaker_index: int = 0) -> Speech:
    return Speech(
        samples=np.zeros(1, dtype=np.float32),
        sample_rate=16000,
        start_timestamp=start,
        end_timestamp=end,
        speaker_index=speaker_index,
    )


def _make_embedding(vector: list[float]) -> Embedding:
    return Embedding.from_numpy(
        kind="speaker",
        space_id="test",
        vector=np.asarray(vector, dtype=np.float32),
        metadata={},
    )


def _make_event(
    speech: Speech, *, text: str = "hello", embedding: Embedding | None = None
) -> STTAudioEvent:
    return STTAudioEvent(
        consumer_name="stt",
        speech=speech,
        text=text,
        embedding=embedding,
    )


def test_create_returns_stt_bundler_instance() -> None:
    bundler = create_stt_audio_event_bundler()
    assert isinstance(bundler, STTAudioEventBundler)


def test_bundle_returns_none_for_empty_events() -> None:
    bundler = create_stt_audio_event_bundler()
    assert bundler.bundle([]) is None


def test_bundle_ignores_non_stt_events() -> None:
    bundler = create_stt_audio_event_bundler()

    ambient_event = AmbientAudioEvent(
        consumer_name="ambient",
        start_timestamp=0.0,
        end_timestamp=1.0,
        predictions=[],
        embedding=_make_embedding([1.0, 0.0]),
    )

    assert bundler.bundle([ambient_event]) is None


def test_bundle_formats_srt_transcript_without_diarization() -> None:
    bundler = create_stt_audio_event_bundler()

    events: list[AudioEvent] = [
        _make_event(_make_speech(0.0, 1.0), text="first"),
        _make_event(_make_speech(1.0, 2.0), text="second"),
    ]

    bundle = bundler.bundle(events)

    assert isinstance(bundle, FileBundle)
    assert len(bundle.manifest.contents) == 1

    content = bundle.manifest.contents[0]
    assert isinstance(content, FileBundleTextContent)
    assert content.visibility == "unsupported"

    transcript = content.text
    assert transcript.startswith("<transcript>")
    assert transcript.endswith("</transcript>")
    assert "first" in transcript
    assert "second" in transcript
    # SRT cue lines, file-relative timestamps.
    cues = re.findall(
        r"^(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> \d{2}:\d{2}:\d{2},\d{3}$",
        transcript,
        flags=re.MULTILINE,
    )
    assert len(cues) == 2
    # No diarization → no speaker label prefix.
    assert "[Speaker" not in transcript
    assert "[silence]" not in transcript
    assert "[overlap]" not in transcript


def test_bundle_labels_speakers_silence_and_overlap_with_embedding() -> None:
    bundler = create_stt_audio_event_bundler()

    events: list[AudioEvent] = [
        _make_event(
            _make_speech(0.0, 0.5, speaker_index=0),
            text="hi",
            embedding=_make_embedding([1.0, 0.0]),
        ),
        _make_event(
            _make_speech(0.5, 1.0, speaker_index=-1),
            text="...",
            embedding=_make_embedding([0.0, 0.0]),
        ),
        _make_event(
            _make_speech(1.0, 1.5, speaker_index=-2),
            text="??",
            embedding=_make_embedding([0.0, 0.0]),
        ),
        _make_event(
            _make_speech(1.5, 2.0, speaker_index=1),
            text="yo",
            embedding=_make_embedding([0.0, 1.0]),
        ),
    ]

    bundle = bundler.bundle(events)
    assert bundle is not None
    transcript = bundle.manifest.contents[0].text  # type: ignore[union-attr]

    assert "[Speaker 1] hi" in transcript
    assert "[silence] ..." in transcript
    assert "[overlap] ??" in transcript
    assert "[Speaker 2] yo" in transcript


def test_bundle_combines_with_other_file_bundles_via_addition() -> None:
    stt = create_stt_audio_event_bundler()
    ambient = create_ambient_audio_event_bundler()

    stt_events: list[AudioEvent] = [_make_event(_make_speech(0.0, 1.0), text="merged")]
    ambient_events: list[AudioEvent] = [
        AmbientAudioEvent(
            consumer_name="ambient",
            start_timestamp=0.0,
            end_timestamp=1.0,
            predictions=[],
            embedding=_make_embedding([1.0, 0.0]),
        )
    ]

    stt_bundle = stt.bundle(stt_events)
    ambient_bundle = ambient.bundle(ambient_events)

    assert stt_bundle is not None
    assert ambient_bundle is not None

    merged = stt_bundle + ambient_bundle

    # both content entries are preserved in declaration order.
    assert len(merged.manifest.contents) == 2
    assert merged.manifest.contents[0].text.startswith("<transcript>")  # type: ignore[union-attr]
    assert merged.manifest.contents[1].text.startswith("<ambient>")  # type: ignore[union-attr]
