from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_lc_openai_chat_provider import create_lc_openai_chat_provider
    from ._models.lc_openai_chat_provider import LCOpenAIChatProvider
    from ._settings import LCOpenAIChatProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_lc_openai_chat_provider",
    # ._models
    "LCOpenAIChatProvider",
    # ._settings
    "LCOpenAIChatProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_lc_openai_chat_provider": "._helpers.create_lc_openai_chat_provider",
        # ._models
        "LCOpenAIChatProvider": "._models.lc_openai_chat_provider",
        # ._settings
        "LCOpenAIChatProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
