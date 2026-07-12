from collections.abc import Iterator

import pytest

from kiarina.agi.ocr_model import ocr_model_registry, settings_manager


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "default": "custom-default",
        "presets": {
            "custom-default": {
                "provider_name": "mock",
            }
        },
    }
    yield
    settings_manager.cli_args = {}


def test_default() -> None:
    ocr_model = ocr_model_registry.resolve()
    assert ocr_model.name == "custom-default"
    assert ocr_model.provider_name == "mock"
