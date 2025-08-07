# app/memory/short_term.py
from typing import Dict
from app.memory.backends import STMBackend, InMemorySTMBackend, RedisSTMBackend
from app.memory.schema import ShortTermMemoryEntry
from app.config import settings


class ShortTermMemory:
    def __init__(
        self, backend: STMBackend = None, ttl_minutes: int = settings.STM_TTL_MINUTES
    ):
        self.backend = backend or InMemorySTMBackend(ttl_minutes)

    def set(self, session_id: str, key: str, value: str):
        entry = ShortTermMemoryEntry(session_id=session_id, key=key, value=value)
        self.backend.set(session_id, key, entry)

    def get(self, session_id: str, key: str) -> str:
        entry = self.backend.get(session_id, key)
        return entry.value if entry else ""

    def get_all(self, session_id: str) -> Dict[str, str]:
        entries = self.backend.get_all(session_id)
        return {k: v.value for k, v in entries.items()}

    def clear(self, session_id: str):
        self.backend.clear(session_id)

    def cleanup_expired(self):
        self.backend.cleanup_expired()
