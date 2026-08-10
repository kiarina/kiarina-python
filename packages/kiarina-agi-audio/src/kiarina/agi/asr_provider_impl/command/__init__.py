from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_command_asr_provider import create_command_asr_provider
    from ._models.command_asr_provider import CommandASRProvider
    from ._settings import CommandASRProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_command_asr_provider",
    # ._models
    "CommandASRProvider",
    # ._settings
    "CommandASRProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_command_asr_provider": "._helpers.create_command_asr_provider",
        # ._models
        "CommandASRProvider": "._models.command_asr_provider",
        # ._settings
        "CommandASRProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
