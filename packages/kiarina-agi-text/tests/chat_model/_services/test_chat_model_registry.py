from collections.abc import Iterator

import pytest

from kiarina.agi.chat_model import chat_model_registry, settings_manager


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "default": "my",
        "aliases": {
            "alias": "my",
        },
        "presets": {
            "my": {
                "provider_name": "my",
                "provider_config": {
                    "context_window": 1024,
                    "max_output_tokens": 256,
                },
            }
        },
        "customs": {
            "custom": {
                "provider_name": "my",
                "provider_config": {
                    "context_window": 1024,
                    "max_output_tokens": 256,
                },
            }
        },
    }
    yield
    settings_manager.cli_args = {}


def test_default() -> None:
    chat_model = chat_model_registry.resolve()
    assert chat_model.name == "my"


def test_alias() -> None:
    chat_model = chat_model_registry.resolve("alias")
    assert chat_model.name == "my"


def test_preset() -> None:
    chat_model = chat_model_registry.resolve("my")
    assert chat_model.name == "my"


def test_custom() -> None:
    chat_model = chat_model_registry.resolve("custom")
    assert chat_model.name == "custom"


def test_config() -> None:
    chat_model = chat_model_registry.resolve(
        context_window=2048,
        token_count_limit=1500,
    )
    chat_model.config.token_scale_factor = 0.8

    assert chat_model.provider_config.get("context_window") == 2048
    assert chat_model.provider_config.get("token_count_limit") == 1500
    assert chat_model.token_scale_factor == 0.8


def test_config_string() -> None:
    chat_model = chat_model_registry.resolve("my?max_output_tokens=128")
    assert chat_model.provider_config.get("max_output_tokens") == 128
