from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_vad_provider import create_mock_vad_provider
    from ._models.mock_vad_provider import MockVADProvider
    from ._settings import MockVADProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_mock_vad_provider",
    # ._models
    "MockVADProvider",
    # ._settings
    "MockVADProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_mock_vad_provider": "._helpers.create_mock_vad_provider",
        # ._models
        "MockVADProvider": "._models.mock_vad_provider",
        # ._settings
        "MockVADProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
