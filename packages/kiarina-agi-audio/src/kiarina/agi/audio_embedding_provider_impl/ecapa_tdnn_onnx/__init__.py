from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_ecapa_tdnn_onnx_audio_embedding_provider import (
        create_ecapa_tdnn_onnx_audio_embedding_provider,
    )
    from ._models.ecapa_tdnn_onnx_audio_embedding_provider import (
        EcapaTDNNOnnxAudioEmbeddingProvider,
    )
    from ._settings import (
        EcapaTDNNOnnxAudioEmbeddingProviderSettings,
        settings_manager,
    )

__all__ = [
    # ._helpers
    "create_ecapa_tdnn_onnx_audio_embedding_provider",
    # ._models
    "EcapaTDNNOnnxAudioEmbeddingProvider",
    # ._settings
    "EcapaTDNNOnnxAudioEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_ecapa_tdnn_onnx_audio_embedding_provider": "._helpers.create_ecapa_tdnn_onnx_audio_embedding_provider",
        # ._models
        "EcapaTDNNOnnxAudioEmbeddingProvider": "._models.ecapa_tdnn_onnx_audio_embedding_provider",
        # ._settings
        "EcapaTDNNOnnxAudioEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
