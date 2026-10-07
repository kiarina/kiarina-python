import asyncio
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any

from .codex_app_server_session import CodexAppServerSession


@dataclass
class LiveThread:
    """
    A `codex app-server` process kept alive with its thread, so the next request
    can continue it instead of starting a new thread, and read the prompt cache.
    """

    session: CodexAppServerSession

    directory: tempfile.TemporaryDirectory[str]
    """The process's working directory, which holds its model catalog."""

    thread_id: str = ""

    turn_id: str = ""

    turn_completed: bool = False

    held_requests: dict[str, Any] = field(default_factory=dict)
    """Tool call requests left unanswered: call id to request id."""

    pending_call_ids: list[str] = field(default_factory=list)
    """The tool calls of the last response. The turn waits for their results."""

    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    """Tool call results to answer with: call id to the reply."""

    next_items: list[dict[str, Any]] = field(default_factory=list)
    """Items to inject before the next turn, when the last turn completed."""

    history_hash: str = ""
    """The history hash of the AI message this thread can continue from."""

    expires_at: float = 0.0

    loop: asyncio.AbstractEventLoop | None = None

    def is_usable(self) -> bool:
        try:
            running = asyncio.get_running_loop()
        except RuntimeError:  # pragma: no cover
            return False

        return self.loop is running and time.monotonic() < self.expires_at

    async def close(self) -> None:
        try:
            await self.session.close()
        finally:
            self.directory.cleanup()

    def kill(self) -> None:
        self.session.kill()
        self.directory.cleanup()
