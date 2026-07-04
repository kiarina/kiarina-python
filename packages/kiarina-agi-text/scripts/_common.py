import os
from pathlib import Path

from kiarina.agi.chat_model import settings_manager as chat_model_settings_manager
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure


def configure_script() -> RunContext:
    configure(app_author="kiarina", app_name="kiarina-agi-text")

    chat_model_name = (
        os.getenv("KIARINA_AGI_TEXT_TEST_CHAT_MODEL", "mock").strip() or "mock"
    )
    settings = chat_model_settings_manager.settings_cls().model_dump()
    settings["default"] = chat_model_name
    chat_model_settings_manager.cli_args = settings

    return RunContext(
        organization_id="kiarina.agi",
        user_id="scripts",
        agent_id=Path(__file__).stem,
        node_id="scripts",
    )


def read_large_text() -> str:
    path = Path(__file__).parents[3] / "tests/assets/txt/utf-8_1027line_125kb.txt"
    return path.read_text()
