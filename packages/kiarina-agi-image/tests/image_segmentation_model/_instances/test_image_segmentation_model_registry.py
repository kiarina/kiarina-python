from collections.abc import Iterator

import pytest

from kiarina.agi.image_segmentation_model import (
    image_segmentation_model_registry,
    settings_manager,
)


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {"default": "birefnet"}
    yield
    settings_manager.cli_args = {}


def test_default() -> None:
    model = image_segmentation_model_registry.resolve()

    assert model.name == "birefnet"
    assert model.provider_name == "birefnet"


def test_provider_config() -> None:
    model = image_segmentation_model_registry.resolve("birefnet?threshold=0.8")

    assert model.provider_config == {"threshold": 0.8}
