from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._exceptions.chat_proxy_error import ChatProxyError
    from ._exceptions.chat_proxy_missing_files_error import ChatProxyMissingFilesError
    from ._helpers.create_chat_proxy_app import create_chat_proxy_app
    from ._helpers.run_chat_proxy import run_chat_proxy
    from ._operations.attach_chat_proxy_files import attach_chat_proxy_files
    from ._operations.collect_chat_proxy_files import collect_chat_proxy_files
    from ._schemas.chat_proxy_error_info import ChatProxyErrorInfo
    from ._schemas.chat_proxy_event import ChatProxyEvent
    from ._schemas.chat_proxy_file import ChatProxyFile
    from ._schemas.chat_proxy_model_info import ChatProxyModelInfo
    from ._schemas.chat_proxy_request import ChatProxyRequest
    from ._settings import ChatProxySettings, settings_manager

__all__ = [
    # ._exceptions
    "ChatProxyError",
    "ChatProxyMissingFilesError",
    # ._helpers
    "create_chat_proxy_app",
    "run_chat_proxy",
    # ._operations
    "attach_chat_proxy_files",
    "collect_chat_proxy_files",
    # ._schemas
    "ChatProxyErrorInfo",
    "ChatProxyEvent",
    "ChatProxyFile",
    "ChatProxyModelInfo",
    "ChatProxyRequest",
    # ._settings
    "ChatProxySettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._exceptions
        "ChatProxyError": "._exceptions.chat_proxy_error",
        "ChatProxyMissingFilesError": "._exceptions.chat_proxy_missing_files_error",
        # ._helpers
        "create_chat_proxy_app": "._helpers.create_chat_proxy_app",
        "run_chat_proxy": "._helpers.run_chat_proxy",
        # ._operations
        "attach_chat_proxy_files": "._operations.attach_chat_proxy_files",
        "collect_chat_proxy_files": "._operations.collect_chat_proxy_files",
        # ._schemas
        "ChatProxyErrorInfo": "._schemas.chat_proxy_error_info",
        "ChatProxyEvent": "._schemas.chat_proxy_event",
        "ChatProxyFile": "._schemas.chat_proxy_file",
        "ChatProxyModelInfo": "._schemas.chat_proxy_model_info",
        "ChatProxyRequest": "._schemas.chat_proxy_request",
        # ._settings
        "ChatProxySettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
