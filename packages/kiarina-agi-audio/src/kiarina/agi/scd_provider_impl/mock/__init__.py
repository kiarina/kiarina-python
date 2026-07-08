from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_scd_provider import create_mock_scd_provider
    from ._models.mock_scd_provider import MockSCDProvider
    from ._settings import MockSCDProviderSettings, settings_manager

__all__ = [
    "create_mock_scd_provider",
    "MockSCDProvider",
    "MockSCDProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_mock_scd_provider": "._helpers.create_mock_scd_provider",
        "MockSCDProvider": "._models.mock_scd_provider",
        "MockSCDProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
