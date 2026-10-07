from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import FileType


class ClaudeCodeChatProviderSettings(ChatCapabilities, BaseSettings):
    """
    Runs Claude Code through the Claude Agent SDK with its own login (a Claude
    subscription), one new session per request.
    """

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_CLAUDE_CODE_",
        extra="ignore",
    )

    model_name: str = "claude-sonnet-5-5"

    effort: Literal["low", "medium", "high", "xhigh", "max"] | None = None

    context_window: int = 200_000

    token_count_limit: int = 160_000

    image_file_count_limit: int = 100

    pdf_page_count_limit: int = 100

    input_enabled: dict[FileType, bool] = {
        "image": True,
        "pdf": True,
    }

    output_enabled: dict[FileType, bool] = {
        "image": True,
    }

    parallel_tool_calls: bool | None = True

    timeout: float | None = 600.0

    cli_path: str | None = None
    """Claude Code to run. The SDK's bundled one when unset."""

    env: dict[str, str] = {}
    """Environment variables for Claude Code, applied after the inherited ones are cleared."""


settings_manager = SettingsManager(ClaudeCodeChatProviderSettings)
