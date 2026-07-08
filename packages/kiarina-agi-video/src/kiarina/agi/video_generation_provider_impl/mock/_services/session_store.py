import asyncio
import time
from dataclasses import dataclass, field
from typing import Self

from kiarina.agi.video_generation_provider import VideoGenerationSessionID


class SessionStore:
    _instance: Self | None = None

    @dataclass
    class SessionData:
        session_id: VideoGenerationSessionID
        prompt: str
        timestamp: float = field(default_factory=time.time)
        delay_seconds: float = 0.1

    def __init__(self) -> None:
        self._sessions: dict[VideoGenerationSessionID, SessionStore.SessionData] = {}
        self._lock = asyncio.Lock()

    async def create(
        self,
        session_id: VideoGenerationSessionID,
        prompt: str,
        *,
        delay_seconds: float = 0.1,
    ) -> SessionData:
        async with self._lock:
            session = self.SessionData(
                session_id=session_id,
                prompt=prompt,
                delay_seconds=delay_seconds,
            )
            self._sessions[session_id] = session
            return session

    async def get(self, session_id: VideoGenerationSessionID) -> SessionData | None:
        async with self._lock:
            return self._sessions.get(session_id)

    async def is_completed(self, session_id: VideoGenerationSessionID) -> bool:
        session = await self.get(session_id)

        if not session:
            return False

        elapsed = time.time() - session.timestamp
        return elapsed >= session.delay_seconds

    async def delete(self, session_id: VideoGenerationSessionID) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def clear(self) -> None:
        async with self._lock:
            self._sessions.clear()

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance
