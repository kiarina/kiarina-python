import os
import re
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure, reset
from kiarina.utils.file import FileBlob, read_file


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-audio")
    yield
    reset()


@pytest.fixture(autouse=True)
def skip_costly(request: pytest.FixtureRequest) -> None:
    if (
        request.node.get_closest_marker("costly")
        and os.getenv("KIARINA_TEST_COSTLY", "0") != "1"
    ):
        pytest.skip("Set KIARINA_TEST_COSTLY=1 to run this test.")


@pytest.fixture(autouse=True)
def skip_downloads_model_on_github_actions(request: pytest.FixtureRequest) -> None:
    if (
        request.node.get_closest_marker("downloads_model")
        and os.getenv("GITHUB_ACTIONS") == "true"
    ):
        pytest.skip("Model download tests are skipped on GitHub Actions.")


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parents[3] / "tests" / "assets"


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture
async def cost_recorder(run_context: RunContext) -> AsyncIterator[object]:
    from kiarina.agi.cost_recorder_impl.null import NullCostRecorder

    recorder = NullCostRecorder()
    yield recorder
    await recorder.flush(run_context)


@pytest.fixture
def audio_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "mp3" / "tone_2s_16kb.mp3")


@pytest.fixture
def speech_audio_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "mp3" / "tone_2s_16kb.mp3")


@pytest.fixture
def audio_file_blob(audio_file_path: str) -> FileBlob:
    file_blob = read_file(audio_file_path)
    assert file_blob is not None
    return file_blob


@pytest.fixture
def audio_samples(audio_file_path: str) -> tuple[np.ndarray, int]:
    return load_audio_samples(audio_file_path)


@pytest.fixture
def multi_speaker_audio_samples(audio_file_path: str) -> tuple[np.ndarray, int]:
    return load_audio_samples(audio_file_path)


def load_audio_samples(path: str | Path) -> tuple[np.ndarray, int]:
    sf = pytest.importorskip("soundfile")

    samples, sample_rate = sf.read(path, dtype="float32", always_2d=True)
    mono = np.asarray(samples, dtype=np.float32).mean(axis=1)
    return mono, int(sample_rate)
