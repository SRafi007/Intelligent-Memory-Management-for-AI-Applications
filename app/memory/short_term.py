# app/memory/short_term.py

from typing import Dict, Any
from app.memory.schema import ShortTermMemoryEntry
from datetime import datetime, timedelta

try:
    from app.memory.backends.redis_backend import RedisSTMBackend

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ShortTermMemory:
    def __init__(self, ttl_minutes: int = 30, use_redis: bool = False):
        self.ttl = timedelta(minutes=ttl_minutes)

        if use_redis and REDIS_AVAILABLE:
            self.backend = RedisSTMBackend()
            self._use_redis = True
        else:
            self._store: Dict[str, Dict[str, ShortTermMemoryEntry]] = {}
            self._use_redis = False

    def set(self, session_id: str, key: str, value: str):
        if self._use_redis:
            self.backend.set(session_id, key, value)
        else:
            entry = ShortTermMemoryEntry(session_id=session_id, key=key, value=value)
            self._store.setdefault(session_id, {})[key] = entry

    def get(self, session_id: str, key: str) -> str:
        if self._use_redis:
            return self.backend.get(session_id, key)
        else:
            # Your existing logic stays the same
            session_data = self._store.get(session_id, {})
            entry = session_data.get(key)
            if entry and not self._is_expired(entry.timestamp):
                return entry.value
            return ""

    def get_all(self, session_id: str) -> Dict[str, str]:
        session_data = self._store.get(session_id, {})
        return {
            k: v.value
            for k, v in session_data.items()
            if not self._is_expired(v.timestamp)
        }

    def clear(self, session_id: str):
        if session_id in self._store:
            del self._store[session_id]

    def _is_expired(self, timestamp: datetime) -> bool:
        return datetime.now(timestamp.tzinfo) - timestamp > self.ttl
