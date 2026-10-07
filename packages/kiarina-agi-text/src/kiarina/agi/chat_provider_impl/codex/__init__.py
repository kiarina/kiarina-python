from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_codex_chat_provider import (
        create_codex_chat_provider,
    )
    from ._models.codex_chat_provider import CodexChatProvider
    from ._settings import CodexChatProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_codex_chat_provider",
    # ._models
    "CodexChatProvider",
    # ._settings
    "CodexChatProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_codex_chat_provider": "._helpers.create_codex_chat_provider",
        # ._models
        "CodexChatProvider": "._models.codex_chat_provider",
        # ._settings
        "CodexChatProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
