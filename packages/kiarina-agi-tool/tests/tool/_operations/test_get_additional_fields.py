from collections.abc import Iterator

import pytest

from kiarina.agi.tool import AdditionalFieldConfig, settings_manager
from kiarina.agi.tool._operations.get_additional_fields import (
    get_additional_fields,
)


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "additional_fields": [
            AdditionalFieldConfig(
                name="test_field",
                type_hint="str",
                description="A test field",
                apply_to=["hello"],
            )
        ]
    }
    yield
    settings_manager.cli_args = {}


def test_none() -> None:
    additional_fields = get_additional_fields("world")
    assert len(additional_fields) == 0


def test_existing() -> None:
    additional_fields = get_additional_fields("hello")
    assert len(additional_fields) == 1
    assert additional_fields[0].name == "test_field"
    assert additional_fields[0].type_hint == "str"
    assert additional_fields[0].description == "A test field"
    print(additional_fields[0].model_dump_json(indent=2))
