from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.parse_srt import parse_srt
    from ._instances.asr_provider_registry import asr_provider_registry
    from ._models.base_asr_provider import BaseASRProvider
    from ._schemas.asr_segment import ASRSegment
    from ._settings import ASRProviderSettings, settings_manager
    from ._types.asr_provider import ASRProvider
    from ._types.asr_provider_name import ASRProviderName
    from ._utils.encode_wav import encode_wav
    from ._utils.format_time import format_time
    from ._utils.write_wav import write_wav

__all__ = [
    # ._helpers
    "parse_srt",
    # ._models
    "BaseASRProvider",
    # ._schemas
    "ASRSegment",
    # ._instances
    "asr_provider_registry",
    # ._settings
    "ASRProviderSettings",
    "settings_manager",
    # ._types
    "ASRProvider",
    "ASRProviderName",
    # ._utils
    "format_time",
    "write_wav",
    "encode_wav",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "parse_srt": "._helpers.parse_srt",
        # ._models
        "BaseASRProvider": "._models.base_asr_provider",
        # ._schemas
        "ASRSegment": "._schemas.asr_segment",
        # ._instances
        "asr_provider_registry": "._instances.asr_provider_registry",
        # ._settings
        "ASRProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ASRProvider": "._types.asr_provider",
        "ASRProviderName": "._types.asr_provider_name",
        # ._utils
        "encode_wav": "._utils.encode_wav",
        "format_time": "._utils.format_time",
        "write_wav": "._utils.write_wav",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
