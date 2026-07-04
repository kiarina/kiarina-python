# mypy: ignore-errors

from pathlib import Path

import pytest
from pydantic_settings_manager import clear_user_configs, load_user_configs

from kiarina.utils.file import read_yaml_dict


@pytest.fixture(autouse=True)
def test_settings():
    settings_path = Path(__file__).resolve().parent / "test_settings.yaml"
    user_configs = read_yaml_dict(settings_path)

    if not user_configs:
        pytest.skip(f"test_settings.yaml is empty: {settings_path}")

    load_user_configs(user_configs)
    yield
    clear_user_configs(user_configs)
