from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_asr_provider import create_mock_asr_provider
    from ._models.mock_asr_provider import MockASRProvider
    from ._settings import MockASRProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_mock_asr_provider",
    # ._models
    "MockASRProvider",
    # ._settings
    "MockASRProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_mock_asr_provider": "._helpers.create_mock_asr_provider",
        # ._models
        "MockASRProvider": "._models.mock_asr_provider",
        # ._settings
        "MockASRProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
