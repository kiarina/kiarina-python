# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import pytest

from kiarina.agi.image_generation_model import (
    image_generation_model_registry,
    settings_manager,
)


@pytest.fixture(autouse=True)
def setup():
    settings_manager.cli_args = {
        "default": "my",
        "aliases": {
            "alias": "my",
        },
        "presets": {
            "my": {
                "provider_name": "my",
                "provider_config": {
                    "model_name": "my_model",
                },
            }
        },
        "customs": {
            "custom": {
                "provider_name": "my",
                "provider_config": {
                    "model_name": "my_model",
                },
            }
        },
    }
    yield
    settings_manager.cli_args = {}


def test_default() -> None:
    image_generation_model = image_generation_model_registry.resolve()
    assert image_generation_model.name == "my"


def test_alias() -> None:
    image_generation_model = image_generation_model_registry.resolve("alias")
    assert image_generation_model.name == "my"


def test_preset() -> None:
    image_generation_model = image_generation_model_registry.resolve("my")
    assert image_generation_model.name == "my"


def test_custom() -> None:
    image_generation_model = image_generation_model_registry.resolve("custom")
    assert image_generation_model.name == "custom"


def test_config() -> None:
    image_generation_model = image_generation_model_registry.resolve(
        model_name="overridden_model"
    )
    assert (
        image_generation_model.provider_config.get("model_name") == "overridden_model"
    )


def test_config_string() -> None:
    image_generation_model = image_generation_model_registry.resolve(
        "my?size=1024x1024"
    )
    assert image_generation_model.provider_config.get("size") == "1024x1024"
