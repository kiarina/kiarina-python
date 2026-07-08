from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._helpers.create_pyannote_scd_provider import create_pyannote_scd_provider
    from ._models.pyannote_scd_provider import PyannoteSCDProvider
    from ._settings import PyannoteSCDProviderSettings, settings_manager
    from ._types.pyannote_output_kind import PyannoteOutputKind

__all__ = [
    # ._helpers
    "create_pyannote_scd_provider",
    # ._models
    "PyannoteSCDProvider",
    # ._settings
    "PyannoteSCDProviderSettings",
    "settings_manager",
    # ._types
    "PyannoteOutputKind",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_pyannote_scd_provider": "._helpers.create_pyannote_scd_provider",
        # ._models
        "PyannoteSCDProvider": "._models.pyannote_scd_provider",
        # ._settings
        "PyannoteSCDProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "PyannoteOutputKind": "._types.pyannote_output_kind",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
