from pathlib import Path

import pytest
from pydantic_settings_manager import clear_user_configs, load_user_configs

from kiarina.utils.file import read_yaml_dict


@pytest.fixture(autouse=True)
def settings():
    settings_path = Path(__file__).resolve().parent / "test_settings.yaml"
    if not settings_path.is_file():
        pytest.skip(f"test_settings.yaml does not exist: {settings_path}")

    user_configs = read_yaml_dict(settings_path)

    if not user_configs:
        pytest.skip(f"test_settings.yaml is empty: {settings_path}")

    service_account_file = Path(
        user_configs["kiarina.lib.google"]["configs"]["service_account"][
            "service_account_file"
        ]
    ).expanduser()
    if not service_account_file.is_file():
        pytest.skip(f"Service account file does not exist: {service_account_file}")

    load_user_configs(user_configs)
    yield
    clear_user_configs(user_configs)
