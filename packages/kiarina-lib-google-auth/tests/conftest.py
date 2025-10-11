import os
from importlib import import_module

import pytest
from pydantic_settings_manager import SettingsManager

import kiarina.utils.file as kf


@pytest.fixture(scope="session")
def load_settings():
    if "KIARINA_LIB_GOOGLE_AUTH_TEST_SETTINGS_FILE" not in os.environ:
        pytest.skip(
            "Environment variable KIARINA_LIB_GOOGLE_AUTH_TEST_SETTINGS_FILE not set, skipping tests."
        )

    test_settings_file = os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_SETTINGS_FILE"]
    test_settings_file = os.path.expanduser(test_settings_file)

    if not os.path.exists(test_settings_file):
        raise FileNotFoundError(f"Settings file not found: {test_settings_file}")

    user_configs = kf.read_yaml_dict(test_settings_file)

    if not user_configs:
        raise ValueError(f"Settings file is empty or invalid: {test_settings_file}")

    for module_name, user_config in user_configs.items():
        try:
            module = import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Module not found: {module_name}") from e

        settings_manager = getattr(module, "settings_manager", None)

        if not settings_manager:
            raise AttributeError(
                f"Module {module_name} does not have a settings_manager attribute"
            )

        if not isinstance(settings_manager, SettingsManager):
            raise TypeError(
                f"settings_manager in module {module_name} is not an instance of SettingsManager"
            )

        settings_manager.user_config = user_config
