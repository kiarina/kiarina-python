import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.apply_mime_alias import apply_mime_alias
    from ._helpers.create_mime_blob import create_mime_blob
    from ._helpers.detect_mime_type import detect_mime_type
    from ._models.mime_blob import MIMEBlob
    from ._settings import settings_manager
    from ._types.mime_detection_options import MimeDetectionOptions

__version__ = "1.0.0"

__all__ = [
    "apply_mime_alias",
    "create_mime_blob",
    "detect_mime_type",
    "MIMEBlob",
    "settings_manager",
    "MimeDetectionOptions",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "apply_mime_alias": "._helpers.apply_mime_alias",
        "create_mime_blob": "._helpers.create_mime_blob",
        "detect_mime_type": "._helpers.detect_mime_type",
        "MIMEBlob": "._models.mime_blob",
        "settings_manager": "._settings",
        "MimeDetectionOptions": "._types.mime_detection_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
