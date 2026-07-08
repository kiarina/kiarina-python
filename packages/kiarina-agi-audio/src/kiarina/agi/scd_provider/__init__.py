from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.base_scd_provider import BaseSCDProvider
    from ._schemas.scd_result import SCDResult
    from ._services.scd_provider_registry import scd_provider_registry
    from ._settings import SCDProviderSettings, settings_manager
    from ._types.scd_provider import SCDProvider
    from ._types.scd_provider_name import SCDProviderName
    from ._types.speaker_probabilities import SpeakerProbabilities

__all__ = [
    "BaseSCDProvider",
    "SCDResult",
    "scd_provider_registry",
    "SCDProviderSettings",
    "settings_manager",
    "SCDProvider",
    "SCDProviderName",
    "SpeakerProbabilities",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "BaseSCDProvider": "._models.base_scd_provider",
        "SCDResult": "._schemas.scd_result",
        "scd_provider_registry": "._services.scd_provider_registry",
        "SCDProviderSettings": "._settings",
        "settings_manager": "._settings",
        "SCDProvider": "._types.scd_provider",
        "SCDProviderName": "._types.scd_provider_name",
        "SpeakerProbabilities": "._types.speaker_probabilities",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
