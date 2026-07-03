# mypy: ignore-errors

import os

import pytest


def _get_names(env_name: str) -> list[str]:
    return [name.strip() for name in os.getenv(env_name, "").split(",") if name.strip()]


@pytest.fixture(autouse=True)
def setup():
    from kiarina.agi.chat_model import settings_manager

    settings_manager.cli_args = settings_manager.settings_cls().model_dump()
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def setup_cost_logger():
    from kiarina.agi.cost_logger import settings_manager

    settings_manager.cli_args = {"default": "console"}
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def setup_request_logger():
    from kiarina.agi.request_logger import settings_manager

    settings_manager.cli_args = {"default": "console"}
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def disable_request_logger():
    from kiarina.agi.request_logger import settings_manager

    settings_manager.cli_args = {}


def pytest_generate_tests(metafunc):
    from kiarina.agi.chat_model import settings_manager

    if "chat_model_name" in metafunc.fixturenames:
        chat_model_names = _get_names("TEST_CHAT_MODELS")
        chat_provider_names = _get_names("TEST_CHAT_PROVIDERS")
        cases = []

        if chat_model_names:
            for chat_model_name in chat_model_names:
                if chat_model_name in settings_manager.settings_cls().presets.keys():
                    cases.append(chat_model_name)

        elif chat_provider_names:
            for (
                chat_model_name,
                chat_model_config,
            ) in settings_manager.settings_cls().presets.items():
                if (
                    chat_model_config.provider_name in chat_provider_names
                    and chat_model_config.visible
                ):
                    cases.append(chat_model_name)

        else:
            for i, chat_model_name in enumerate(
                settings_manager.settings_cls().presets.keys()
            ):
                chat_model_config = settings_manager.settings_cls().presets[
                    chat_model_name
                ]

                if not chat_model_config.visible:
                    continue

                cases.append(
                    pytest.param(chat_model_name, id=f"{i:02d}. {chat_model_name}")
                )

        metafunc.parametrize("chat_model_name", cases)
