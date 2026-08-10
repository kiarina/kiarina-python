import os
from collections.abc import Iterator
from typing import cast

import pytest
from pydantic_settings_manager import load_user_configs

import kiarina.utils.file as kf
from kiarina.lib.firebase import TokenData


@pytest.fixture(scope="session")
def load_settings() -> None:
    env_var = "KIARINA_LIB_FIREBASE_TEST_SETTINGS_FILE"

    if env_var not in os.environ:
        pytest.skip(f"Environment variable {env_var} not set, skipping tests.")

    test_settings_file = os.environ[env_var]
    test_settings_file = os.path.expanduser(test_settings_file)

    if not os.path.exists(test_settings_file):
        raise FileNotFoundError(f"Settings file not found: {test_settings_file}")

    user_configs = kf.read_yaml_dict(test_settings_file)

    if not user_configs:
        raise ValueError(f"Settings file is empty or invalid: {test_settings_file}")

    load_user_configs(user_configs)


@pytest.fixture(scope="session")
def firebase_app(load_settings: None) -> Iterator[object]:
    """Initialize Firebase Admin SDK once per test session."""
    firebase_admin = pytest.importorskip("firebase_admin")
    credentials = pytest.importorskip("firebase_admin.credentials")

    import kiarina.lib.google

    service_account_file = (
        kiarina.lib.google.settings_manager.get_settings().service_account_file
    )
    assert service_account_file is not None

    # Initialize Firebase Admin SDK (only once per session)
    app = firebase_admin.initialize_app(credentials.Certificate(service_account_file))

    yield app

    # Cleanup after all tests
    firebase_admin.delete_app(app)


@pytest.fixture
def user_id() -> str:
    return "test_user"


@pytest.fixture
def api_key(load_settings: None) -> str:
    from kiarina.lib.firebase import settings_manager

    settings = settings_manager.get_settings()
    return settings.api_key.get_secret_value()


@pytest.fixture
def custom_token(firebase_app: object, user_id: str) -> str:
    auth = pytest.importorskip("firebase_admin.auth")
    return cast(bytes, auth.create_custom_token(user_id)).decode("utf-8")


@pytest.fixture
async def token_data(api_key: str, custom_token: str) -> TokenData:
    from kiarina.lib.firebase import exchange_custom_token

    token_data = await exchange_custom_token(
        custom_token=custom_token,
        api_key=api_key,
    )

    return token_data
