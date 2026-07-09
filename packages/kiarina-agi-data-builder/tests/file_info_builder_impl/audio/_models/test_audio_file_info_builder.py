import json
import shutil
import zipfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf  # type: ignore

from kiarina.agi.audio_embedding_model import AudioEmbeddingOptions
from kiarina.agi.audio_source import AudioChunk
from kiarina.agi.audio_tagging_provider import AudioTagPrediction
from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.speaker_change_detector import Speech
from kiarina.utils.file.asyncio import read_file


async def test_audio_file_builder(run_context: RunContext, test_data_dir: Path) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    print("AudioFileInfo:")
    print(file.file_info.model_dump_json(indent=2))


async def test_audio_file_builder_analysis_bundle(
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    from kiarina.agi.file_info_builder_impl.audio import (
        create_audio_file_info_builder,
    )

    builder = create_audio_file_info_builder(
        analysis_enabled=True,
        audio_source="file?sample_rate=16000",
        audio_consumers=[
            "stt"
            "?vad_model=(mock?sample_rate=16000&speech_probabilities.0=1.0&repeat_last=true)"
            "&scd_model=(mock?default_probability=1.0)"
            "&asr_model=(mock?result_text=mock transcript from audio builder)"
        ],
        audio_event_bundlers=["stt"],
    )

    file = await builder.build(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert file.file_info.intermediate_file_path is not None
    assert file.file_info.intermediate_file_path.endswith(".zip")
    assert file.intermediate_file_blob is not None
    assert file.intermediate_file_blob.mime_type == "application/zip"

    with zipfile.ZipFile(file.file_info.intermediate_file_path) as zip_file:
        manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))
        audio_data = zip_file.read("audio.mp3")

    assert audio_data
    assert len(audio_data) < len(file_blob.raw_data)
    assert audio_data != file_blob.raw_data
    audio_samples, _ = sf.read(BytesIO(audio_data), always_2d=True)
    assert audio_samples.shape[1] == 1
    assert manifest["contents"][0] == {
        "type": "audio",
        "file_path": "audio.mp3",
        "mime_type": "audio/mpeg",
        "visibility": "supported",
    }
    assert manifest["contents"][1]["type"] == "text"
    assert manifest["contents"][1]["visibility"] == "unsupported"
    transcript = manifest["contents"][1]["text"]
    assert "mock transcript from audio builder" in transcript
    # SRT wrapped in <transcript> tags.
    assert transcript.startswith("<transcript>")
    assert transcript.endswith("</transcript>")
    assert " --> " in transcript


async def test_audio_file_builder_analysis_enabled_is_parent_flag(
    monkeypatch: pytest.MonkeyPatch,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    from kiarina.agi.file_info_builder_impl.audio import (
        create_audio_file_info_builder,
    )
    from kiarina.agi.file_info_builder_impl.audio._models import (
        audio_file_info_builder as audio_file_info_builder_module,
    )

    async def fail_build_analysis_enabled(
        *_args: object, **_kwargs: object
    ) -> None:  # pragma: no cover
        raise AssertionError("analysis_enabled must gate the analysis pipeline")

    monkeypatch.setattr(
        audio_file_info_builder_module,
        "build_analysis_enabled",
        fail_build_analysis_enabled,
    )

    builder = create_audio_file_info_builder(
        analysis_enabled=False,
    )

    file = await builder.build(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert (
        file.file_info.intermediate_file_path is None
        or file.file_info.intermediate_file_path.endswith(".mp3")
    )


async def test_audio_file_builder_diarization_enabled_labels_speakers(
    monkeypatch: pytest.MonkeyPatch,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    # Ensure embed_audio is actually invoked (no cached bundle).
    shutil.rmtree(
        create_local_repository(run_context).cache_dir,
        ignore_errors=True,
    )

    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    from kiarina.agi.audio_consumer_impl.stt._models import (
        stt_audio_consumer as stt_audio_consumer_module,
    )
    from kiarina.agi.file_info_builder_impl.audio import (
        create_audio_file_info_builder,
    )

    speeches = [
        Speech(
            samples=np.zeros(1600, dtype=np.float32),
            sample_rate=16000,
            start_timestamp=0.0,
            end_timestamp=0.5,
            speaker_index=0,
        ),
        Speech(
            samples=np.zeros(1600, dtype=np.float32),
            sample_rate=16000,
            start_timestamp=0.5,
            end_timestamp=1.0,
            speaker_index=-1,  # unknown_silence
        ),
        Speech(
            samples=np.zeros(1600, dtype=np.float32),
            sample_rate=16000,
            start_timestamp=1.0,
            end_timestamp=1.5,
            speaker_index=1,
        ),
        Speech(
            samples=np.zeros(1600, dtype=np.float32),
            sample_rate=16000,
            start_timestamp=1.5,
            end_timestamp=2.0,
            speaker_index=-2,  # unknown_overlap
        ),
        Speech(
            samples=np.zeros(1600, dtype=np.float32),
            sample_rate=16000,
            start_timestamp=2.0,
            end_timestamp=2.5,
            speaker_index=0,
        ),
    ]

    class FakeSpeakerChangeDetector:
        async def detect(
            self,
            samples: AudioSamples,
            sample_rate: int,
            start_timestamp: float,
        ) -> list[Speech]:
            return speeches

    monkeypatch.setattr(
        stt_audio_consumer_module,
        "create_speaker_change_detector",
        lambda *_args, **_kwargs: FakeSpeakerChangeDetector(),
    )

    # 1st speaker speech, 2nd speaker speech (new), 3rd speaker speech (same as 1st).
    vectors = [
        np.array([1.0, 0.0, 0.0], dtype=np.float32),
        np.array([0.0, 0.0, 0.0], dtype=np.float32),
        np.array([0.0, 1.0, 0.0], dtype=np.float32),
        np.array([0.0, 0.0, 0.0], dtype=np.float32),
        np.array([1.0, 0.0, 0.0], dtype=np.float32),
    ]
    embed_calls: list[int] = []

    async def fake_embed_audio(
        samples: AudioSamples,
        sample_rate: int,
        *,
        audio_embedding_options: AudioEmbeddingOptions | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding:
        vector = vectors[len(embed_calls)]
        embed_calls.append(len(samples))
        return Embedding.from_numpy(
            kind="speaker",
            space_id="test",
            vector=vector,
            metadata={},
        )

    monkeypatch.setattr(stt_audio_consumer_module, "embed_audio", fake_embed_audio)

    builder = create_audio_file_info_builder(
        analysis_enabled=True,
        audio_source="file?sample_rate=16000",
        audio_consumers=[
            "stt"
            "?diarization_enabled=true"
            "&vad_model=(mock?sample_rate=16000&speech_probabilities.0=1.0&repeat_last=true)"
            "&scd_model=(mock?default_probability=1.0)"
            "&asr_model=(mock?result_text=hello)"
            "&audio_embedding_model=mock"
            "&speaker_similarity_threshold=0.5"
        ],
        audio_event_bundlers=["stt"],
    )

    file = await builder.build(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert file.file_info.intermediate_file_path is not None
    with zipfile.ZipFile(file.file_info.intermediate_file_path) as zip_file:
        manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))

    transcript = manifest["contents"][1]["text"]

    # 3 speaker speeches were embedded; silence/overlap are not embedded.
    assert len(embed_calls) == 5

    # Speaker label is assigned per global identity:
    # 1st and 3rd share the same vector -> [Speaker 1], 2nd is distinct -> [Speaker 2].
    assert transcript.count("[Speaker 1] hello") == 2
    assert transcript.count("[Speaker 2] hello") == 1
    assert "[silence] hello" in transcript
    assert "[overlap] hello" in transcript


async def test_audio_file_builder_diarization_disabled_omits_speaker_labels(
    monkeypatch: pytest.MonkeyPatch,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    shutil.rmtree(
        create_local_repository(run_context).cache_dir,
        ignore_errors=True,
    )

    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    from kiarina.agi.audio_consumer_impl.stt._models import (
        stt_audio_consumer as stt_audio_consumer_module,
    )
    from kiarina.agi.file_info_builder_impl.audio import (
        create_audio_file_info_builder,
    )

    async def fail_embed_audio(
        *_args: object, **_kwargs: object
    ) -> None:  # pragma: no cover
        raise AssertionError(
            "embed_audio must not be called when diarization_enabled=False"
        )

    monkeypatch.setattr(stt_audio_consumer_module, "embed_audio", fail_embed_audio)

    builder = create_audio_file_info_builder(
        analysis_enabled=True,
        audio_source="file?sample_rate=16000",
        audio_consumers=[
            "stt"
            "?vad_model=(mock?sample_rate=16000&speech_probabilities.0=1.0&repeat_last=true)"
            "&scd_model=(mock?default_probability=1.0)"
            "&asr_model=(mock?result_text=hello)"
        ],
        audio_event_bundlers=["stt"],
    )

    file = await builder.build(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert file.file_info.intermediate_file_path is not None
    with zipfile.ZipFile(file.file_info.intermediate_file_path) as zip_file:
        manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))

    transcript = manifest["contents"][1]["text"]
    assert "[Speaker" not in transcript
    assert "[silence]" not in transcript
    assert "[overlap]" not in transcript
    assert "hello" in transcript


async def test_audio_file_builder_ambient_bundle(
    monkeypatch: pytest.MonkeyPatch,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    shutil.rmtree(
        create_local_repository(run_context).cache_dir,
        ignore_errors=True,
    )

    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    from kiarina.agi.audio_consumer_impl.ambient._models import (
        ambient_audio_consumer as ambient_audio_consumer_module,
    )
    from kiarina.agi.file_info_builder_impl.audio import (
        create_audio_file_info_builder,
    )

    async def fake_tag_audio(
        *_args: object, **_kwargs: object
    ) -> list[AudioTagPrediction]:
        return [
            AudioTagPrediction("Music", 0.82),
            AudioTagPrediction("Speech", 0.31),
            AudioTagPrediction("Inside, small room", 0.22),
        ]

    vectors = [
        np.array([1.0, 0.0], dtype=np.float32),
        np.array([1.0, 0.0], dtype=np.float32),
        np.array([0.0, 1.0], dtype=np.float32),
    ]
    embed_calls = 0

    async def fake_embed_audio(*_args: object, **_kwargs: object) -> Embedding:
        nonlocal embed_calls
        vector = vectors[min(embed_calls, len(vectors) - 1)]
        embed_calls += 1
        return Embedding.from_numpy(
            kind="sound",
            space_id="test",
            vector=vector,
            metadata={},
        )

    monkeypatch.setattr(ambient_audio_consumer_module, "tag_audio", fake_tag_audio)
    monkeypatch.setattr(ambient_audio_consumer_module, "embed_audio", fake_embed_audio)

    builder = create_audio_file_info_builder(
        analysis_enabled=True,
        audio_consumers=[
            "ambient"
            "?window_seconds=1.0"
            "&top_k=3"
            "&audio_embedding_model=(mock?kind=sound&dimension=2)"
            "&audio_tagging_model=mock"
        ],
        audio_event_bundlers=["ambient?change_similarity_threshold=0.5"],
    )

    file = await builder.build(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert file.file_info.intermediate_file_path is not None

    with zipfile.ZipFile(file.file_info.intermediate_file_path) as zip_file:
        manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))

    assert manifest["contents"][1]["visibility"] == "always"
    ambient = manifest["contents"][1]["text"]
    assert ambient.startswith("<ambient>")
    assert ambient.endswith("</ambient>")
    assert "[Music] 0.820" in ambient
    assert "[Inside, small room] 0.220" in ambient
    assert '<similarity previous="1.000" />' in ambient
    assert '<change similarity="0.000">ambience changed</change>' in ambient
    assert embed_calls == 3


async def test_audio_file_builder_analysis_reads_audio_source_once(
    monkeypatch: pytest.MonkeyPatch,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    shutil.rmtree(
        create_local_repository(run_context).cache_dir,
        ignore_errors=True,
    )

    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    from kiarina.agi.audio_consumer_impl.ambient._models import (
        ambient_audio_consumer as ambient_audio_consumer_module,
    )
    from kiarina.agi.audio_source import audio_source_registry
    from kiarina.agi.file_info_builder_impl.audio import (
        create_audio_file_info_builder,
    )

    class FakeAudioSource:
        name = "fake"

        def __init__(self) -> None:
            self.open_calls = 0
            self.read_calls = 0

        @asynccontextmanager
        async def open(self, target: object | None) -> AsyncIterator[None]:
            self.open_calls += 1
            yield

        async def read(self, *stop_events: object) -> AsyncIterator[AudioChunk]:
            self.read_calls += 1
            for index in range(2):
                yield AudioChunk(
                    samples=np.ones((1, 16000), dtype=np.float32),
                    sample_rate=16000,
                    timestamp=float(index),
                )

    fake_audio_source = FakeAudioSource()

    async def fake_tag_audio(
        *_args: object, **_kwargs: object
    ) -> list[AudioTagPrediction]:
        return [AudioTagPrediction("Music", 0.82)]

    async def fake_embed_audio(*_args: object, **_kwargs: object) -> Embedding:
        return Embedding.from_numpy(
            kind="sound",
            space_id="test",
            vector=np.array([1.0, 0.0], dtype=np.float32),
            metadata={},
        )

    monkeypatch.setattr(
        audio_source_registry,
        "resolve",
        lambda *_args, **_kwargs: fake_audio_source,
    )
    monkeypatch.setattr(ambient_audio_consumer_module, "tag_audio", fake_tag_audio)
    monkeypatch.setattr(ambient_audio_consumer_module, "embed_audio", fake_embed_audio)

    builder = create_audio_file_info_builder(
        analysis_enabled=True,
        audio_source="fake",
        audio_consumers=[
            "stt"
            "?vad_model=(mock?sample_rate=16000&speech_probabilities.0=1.0&repeat_last=true)"
            "&scd_model=(mock?default_probability=1.0)"
            "&asr_model=(mock?result_text=hello)",
            "ambient?window_seconds=1.0",
        ],
        audio_event_bundlers=["stt", "ambient"],
    )

    file = await builder.build(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    assert fake_audio_source.open_calls == 1
    assert fake_audio_source.read_calls == 1
    assert file.file_info.intermediate_file_path is not None

    with zipfile.ZipFile(file.file_info.intermediate_file_path) as zip_file:
        manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))

    assert manifest["contents"][1]["text"].startswith("<transcript>")
    assert manifest["contents"][2]["text"].startswith("<ambient>")
