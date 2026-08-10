from collections.abc import Iterator
from typing import Any

import pytest

from kiarina.agi.video_generation_model import settings_manager
from kiarina.agi.video_generation_provider_impl import mock


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = settings_manager.settings_cls().model_dump()
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def setup_mock(video_file_path: str) -> None:
    mock.settings_manager.cli_args = {
        "result_video_file_path": video_file_path,
    }


def pytest_generate_tests(metafunc: Any) -> None:
    if "video_generation_model_name" in metafunc.fixturenames:
        cases = []

        for i, video_generation_model_name in enumerate(
            settings_manager.settings_cls().presets.keys()
        ):
            cases.append(
                pytest.param(
                    video_generation_model_name,
                    id=f"{i:02d}. {video_generation_model_name}",
                )
            )

        metafunc.parametrize("video_generation_model_name", cases)
