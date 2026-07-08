from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.tag_audio import tag_audio
    from ._models.audio_tagging_model import AudioTaggingModel
    from ._schemas.audio_tagging_model_config import AudioTaggingModelConfig
    from ._services.audio_tagging_model_registry import audio_tagging_model_registry
    from ._settings import AudioTaggingModelSettings, settings_manager
    from ._types.audio_tagging_model_alias import AudioTaggingModelAlias
    from ._types.audio_tagging_model_name import AudioTaggingModelName
    from ._types.audio_tagging_model_specifier import AudioTaggingModelSpecifier
    from ._types.audio_tagging_options import AudioTaggingOptions

__all__ = [
    "tag_audio",
    "AudioTaggingModel",
    "AudioTaggingModelConfig",
    "audio_tagging_model_registry",
    "AudioTaggingModelSettings",
    "settings_manager",
    "AudioTaggingModelAlias",
    "AudioTaggingModelName",
    "AudioTaggingModelSpecifier",
    "AudioTaggingOptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "tag_audio": "._helpers.tag_audio",
        "AudioTaggingModel": "._models.audio_tagging_model",
        "AudioTaggingModelConfig": "._schemas.audio_tagging_model_config",
        "audio_tagging_model_registry": "._services.audio_tagging_model_registry",
        "AudioTaggingModelSettings": "._settings",
        "settings_manager": "._settings",
        "AudioTaggingModelAlias": "._types.audio_tagging_model_alias",
        "AudioTaggingModelName": "._types.audio_tagging_model_name",
        "AudioTaggingModelSpecifier": "._types.audio_tagging_model_specifier",
        "AudioTaggingOptions": "._types.audio_tagging_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
