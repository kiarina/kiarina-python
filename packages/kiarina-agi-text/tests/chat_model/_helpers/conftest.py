# mypy: ignore-errors

import json

import pytest

from kiarina.agi.message import HumanMessage


@pytest.fixture
def create_tool_call_message(chat_model_name: str):
    def create(text: str, *tool_names: str) -> HumanMessage:
        if chat_model_name != "mock":
            return HumanMessage.create(text)

        return HumanMessage.create(
            json.dumps(
                {
                    "tool_calls": [
                        {
                            "name": tool_name,
                            "args": {"reason": "test"},
                        }
                        for tool_name in tool_names
                    ]
                }
            )
        )

    return create


@pytest.fixture(autouse=True)
def setup(chat_model_name: str):
    from kiarina.agi.chat_model import settings_manager

    settings = settings_manager.settings_cls().model_dump()
    settings["default"] = chat_model_name
    settings_manager.cli_args = settings
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
