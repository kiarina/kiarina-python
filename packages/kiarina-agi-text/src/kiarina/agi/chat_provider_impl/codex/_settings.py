from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import FileType


class CodexChatProviderSettings(ChatCapabilities, BaseSettings):
    """
    Runs `codex app-server` with its own login (a ChatGPT subscription), one new
    process and thread per request.
    """

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_CODEX_",
        extra="ignore",
    )

    model_name: str = "gpt-6.1-sol"

    reasoning_effort: (
        Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"] | None
    ) = "low"

    context_window: int = 272_000
    """The subscription's window in Codex's model list, smaller than the API's."""

    token_count_limit: int = 240_000

    image_file_count_limit: int = 100

    input_enabled: dict[FileType, bool] = {
        "image": True,
    }

    output_enabled: dict[FileType, bool] = {
        "image": True,
    }

    timeout: float | None = 600.0

    thread_reuse: bool = True
    """
    Keep the process and thread after a response, and continue them when the next
    request extends the same history. Codex reads the prompt cache only within a
    thread.
    """

    thread_idle_timeout: float = 600.0
    """Seconds a kept thread waits for the next request before it is stopped."""

    max_live_threads: int = 4
    """Kept threads per process. The oldest is stopped beyond this."""

    codex_bin: str | None = None
    """Codex to run. The one bundled in `openai-codex-cli-bin` when unset."""

    codex_home: str | None = None
    """Codex's home with the login and model list. `CODEX_HOME` or `~/.codex` when unset."""

    config_overrides: list[str] = []
    """Extra `--config key=value` overrides, applied after the provider's own."""

    env: dict[str, str] = {}
    """Extra environment variables for Codex."""


settings_manager = SettingsManager(CodexChatProviderSettings)
