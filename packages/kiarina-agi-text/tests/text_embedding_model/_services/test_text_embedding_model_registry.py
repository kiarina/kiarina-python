# mypy: ignore-errors

import pytest

from kiarina.agi.text_embedding_model import (
    settings_manager,
    text_embedding_model_registry,
)


@pytest.fixture(autouse=True)
def setup():
    settings_manager.cli_args = {
        "presets": {
            "my": {
                "provider_name": "mock",
                "provider_config": {"dimension": 2, "embedding": [3.0, 4.0]},
            }
        },
        "customs": {
            "custom": {
                "provider_name": "mock",
                "provider_config": {"dimension": 2, "embedding": [5.0, 12.0]},
            }
        },
    }
    yield
    settings_manager.cli_args = {}


def test_preset() -> None:
    text_embedding_model = text_embedding_model_registry.resolve("my")
    assert text_embedding_model.name == "my"


def test_custom() -> None:
    text_embedding_model = text_embedding_model_registry.resolve("custom")
    assert text_embedding_model.name == "custom"


def test_config() -> None:
    text_embedding_model = text_embedding_model_registry.resolve("my", dimension=3)
    assert text_embedding_model.provider_config.get("dimension") == 3


def test_config_string() -> None:
    text_embedding_model = text_embedding_model_registry.resolve("my?dimension=4")
    assert text_embedding_model.provider_config.get("dimension") == 4
