from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_video_generation_provider import (
        create_mock_video_generation_provider,
    )
    from ._models.mock_video_generation_provider import MockVideoGenerationProvider
    from ._services.session_store import SessionStore
    from ._settings import MockVideoGenerationProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_mock_video_generation_provider",
    # ._models
    "MockVideoGenerationProvider",
    # ._services
    "SessionStore",
    # ._settings
    "MockVideoGenerationProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_mock_video_generation_provider": "._helpers.create_mock_video_generation_provider",
        # ._models
        "MockVideoGenerationProvider": "._models.mock_video_generation_provider",
        # ._services
        "SessionStore": "._services.session_store",
        # ._settings
        "MockVideoGenerationProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
