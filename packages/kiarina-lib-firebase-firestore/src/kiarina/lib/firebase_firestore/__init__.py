import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._helpers.get_document import get_document
    from ._helpers.list_documents import list_documents
    from ._schemas.document_list import DocumentList
    from ._schemas.document_snapshot import DocumentSnapshot
    from ._settings import FirestoreSettings, settings_manager

__all__ = [
    # ._helpers
    "get_document",
    "list_documents",
    # ._schemas
    "DocumentList",
    "DocumentSnapshot",
    # ._settings
    "FirestoreSettings",
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "get_document": "._helpers.get_document",
        "list_documents": "._helpers.list_documents",
        # ._schemas
        "DocumentList": "._schemas.document_list",
        "DocumentSnapshot": "._schemas.document_snapshot",
        # ._settings
        "FirestoreSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
