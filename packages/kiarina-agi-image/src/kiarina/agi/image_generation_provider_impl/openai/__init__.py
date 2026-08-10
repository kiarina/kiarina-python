from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_openai_image_generation_provider import (
        create_openai_image_generation_provider,
    )
    from ._models.openai_image_generation_provider import OpenAIImageGenerationProvider
    from ._settings import OpenAIImageGenerationProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_openai_image_generation_provider",
    # ._models
    "OpenAIImageGenerationProvider",
    # ._settings
    "OpenAIImageGenerationProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_openai_image_generation_provider": "._helpers.create_openai_image_generation_provider",
        # ._models
        "OpenAIImageGenerationProvider": "._models.openai_image_generation_provider",
        # ._settings
        "OpenAIImageGenerationProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
