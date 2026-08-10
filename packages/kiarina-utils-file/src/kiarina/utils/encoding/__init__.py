import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.decode_binary_to_text import decode_binary_to_text
    from ._helpers.detect_encoding import detect_encoding
    from ._helpers.get_default_encoding import get_default_encoding
    from ._helpers.is_binary import is_binary
    from ._settings import settings_manager
    from ._utils.normalize_newlines import normalize_newlines

__version__ = "1.0.0"

__all__ = [
    "decode_binary_to_text",
    "detect_encoding",
    "get_default_encoding",
    "is_binary",
    "settings_manager",
    "normalize_newlines",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "decode_binary_to_text": "._helpers.decode_binary_to_text",
        "detect_encoding": "._helpers.detect_encoding",
        "get_default_encoding": "._helpers.get_default_encoding",
        "is_binary": "._helpers.is_binary",
        "settings_manager": "._settings",
        "normalize_newlines": "._utils.normalize_newlines",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
