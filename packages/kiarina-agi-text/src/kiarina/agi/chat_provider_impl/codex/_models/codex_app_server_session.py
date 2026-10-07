import asyncio
import contextlib
import json
from collections import deque
from typing import Any

_STREAM_LIMIT = 64 * 1024 * 1024
"""One JSON-RPC message per line. A response item can carry a large prompt."""


class CodexAppServerSession:
    """
    A `codex app-server` process spoken to with JSON-RPC over stdio.

    Notifications and requests from the server are queued in order and never
    answered. Holding a tool call request keeps Codex from running the tool and
    from sending the model a second request.
    """

    def __init__(self, args: list[str], *, env: dict[str, str], cwd: str) -> None:
        self._args = args
        self._env = env
        self._cwd = cwd
        self._process: asyncio.subprocess.Process | None = None
        self._next_id = 0
        self._pending: dict[int, asyncio.Future[Any]] = {}
        self._events: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._stderr_tail: deque[str] = deque(maxlen=40)
        self._tasks: list[asyncio.Task[None]] = []

    @property
    def stderr_tail(self) -> str:
        return "\n".join(self._stderr_tail)

    async def start(self) -> None:
        self._process = await asyncio.create_subprocess_exec(
            *self._args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self._env,
            cwd=self._cwd,
            limit=_STREAM_LIMIT,
        )
        self._tasks = [
            asyncio.create_task(self._read_stdout()),
            asyncio.create_task(self._read_stderr()),
        ]

    async def request(self, method: str, params: dict[str, Any] | None) -> Any:
        self._next_id += 1
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._pending[self._next_id] = future
        await self._write({"id": self._next_id, "method": method, "params": params})
        return await future

    async def notify(self, method: str, params: dict[str, Any] | None) -> None:
        await self._write({"method": method, "params": params})

    async def respond(self, request_id: Any, result: dict[str, Any]) -> None:
        """Answer a request from the server."""
        await self._write({"id": request_id, "result": result})

    async def next_event(self) -> dict[str, Any]:
        """The next notification or server request: `{"method", "params", ["id"]}`."""
        return await self._events.get()

    async def close(self) -> None:
        process = self._process
        self._process = None

        if process is not None and process.returncode is None:
            if process.stdin is not None:
                process.stdin.close()

            process.terminate()

            try:
                await asyncio.wait_for(process.wait(), timeout=2)
            except TimeoutError:
                process.kill()
                await process.wait()

        for task in self._tasks:
            task.cancel()

            with contextlib.suppress(asyncio.CancelledError):
                await task

    def kill(self) -> None:
        """Stop the process without waiting, for when the event loop is not usable."""
        process = self._process
        self._process = None

        if process is not None and process.returncode is None:
            try:
                process.kill()
            except (ProcessLookupError, RuntimeError):  # pragma: no cover
                pass

        for task in self._tasks:
            if not task.done():
                try:
                    task.cancel()
                except RuntimeError:  # pragma: no cover
                    pass

    async def _write(self, message: dict[str, Any]) -> None:
        if self._process is None or self._process.stdin is None:
            raise RuntimeError("codex app-server is not running")

        self._process.stdin.write((json.dumps(message) + "\n").encode())
        await self._process.stdin.drain()

    async def _read_stdout(self) -> None:
        assert self._process is not None and self._process.stdout is not None
        error: Exception | None = None

        try:
            async for line in self._process.stdout:
                message = json.loads(line)

                if "method" in message:
                    await self._events.put(message)
                    continue

                if future := self._pending.pop(message.get("id"), None):
                    if "error" in message:
                        future.set_exception(
                            RuntimeError(f"codex app-server: {message['error']}")
                        )
                    else:
                        future.set_result(message.get("result"))
        except Exception as e:  # pragma: no cover
            error = e

        closed = RuntimeError(
            f"codex app-server exited. stderr: {self.stderr_tail[-2000:]}"
        )

        if error is not None:  # pragma: no cover
            closed.__cause__ = error

        for future in self._pending.values():
            if not future.done():
                future.set_exception(closed)

        self._pending.clear()
        await self._events.put({"method": "_closed", "params": {}})

    async def _read_stderr(self) -> None:
        assert self._process is not None and self._process.stderr is not None

        async for line in self._process.stderr:
            self._stderr_tail.append(line.decode(errors="replace").rstrip())
