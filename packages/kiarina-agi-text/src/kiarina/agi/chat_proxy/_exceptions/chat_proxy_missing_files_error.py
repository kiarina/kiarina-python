from .chat_proxy_error import ChatProxyError


class ChatProxyMissingFilesError(ChatProxyError):
    """The chat proxy does not have the contents of these files (SHA-256 hashes)."""

    def __init__(self, hashes: list[str]) -> None:
        self.hashes: list[str] = hashes
        super().__init__(f"The chat proxy lacks {len(hashes)} file(s)")
