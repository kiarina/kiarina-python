from .._settings import ChatProxySettings, settings_manager
from .create_chat_proxy_app import create_chat_proxy_app

try:
    import uvicorn
except ImportError as exc:
    raise ImportError(
        "uvicorn is required to run the chat proxy. "
        "Install it with: pip install 'kiarina-agi-text[chat-proxy]'"
    ) from exc


def run_chat_proxy(settings: ChatProxySettings | None = None) -> None:
    if settings is None:
        settings = settings_manager.get_settings()

    uvicorn.run(create_chat_proxy_app(settings), host=settings.host, port=settings.port)
