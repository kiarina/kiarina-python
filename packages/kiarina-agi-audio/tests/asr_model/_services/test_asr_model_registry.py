from collections.abc import Iterator

import pytest

from kiarina.agi.asr_model import asr_model_registry, settings_manager


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "default": "my",
        "aliases": {"alias": "my"},
        "presets": {
            "my": {
                "provider_name": "my",
                "provider_config": {
                    "model_name": "my",
                },
            },
        },
        "customs": {
            "custom": {
                "provider_name": "my",
                "provider_config": {
                    "model_name": "my",
                },
            },
        },
    }
    yield
    settings_manager.cli_args = {}


def test_default() -> None:
    asr_model = asr_model_registry.resolve()
    assert asr_model.name == "my"


def test_alias() -> None:
    asr_model = asr_model_registry.resolve("alias")
    assert asr_model.name == "my"


def test_preset() -> None:
    asr_model = asr_model_registry.resolve("my")
    assert asr_model.name == "my"


def test_custom() -> None:
    asr_model = asr_model_registry.resolve("custom")
    assert asr_model.name == "custom"


def test_config() -> None:
    asr_model = asr_model_registry.resolve("my", language="ja")
    assert asr_model.provider_config.get("language") == "ja"


def test_config_string() -> None:
    asr_model = asr_model_registry.resolve("my?language=ja")
    assert asr_model.provider_config.get("language") == "ja"
