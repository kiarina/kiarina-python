from collections.abc import Iterator

import pytest

from kiarina.agi.asr_model import settings_manager


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = settings_manager.settings_cls().model_dump()
    yield
    settings_manager.cli_args = {}


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "asr_model_name" in metafunc.fixturenames:
        cases: list[object] = []

        for i, asr_model_name in enumerate(settings_manager.settings_cls().presets):
            asr_model_config = settings_manager.settings_cls().presets[asr_model_name]

            if not asr_model_config.visible:
                continue

            cases.append(
                pytest.param(
                    asr_model_name,
                    id=f"{i:02d}. {asr_model_name}",
                )
            )

        metafunc.parametrize("asr_model_name", cases)
