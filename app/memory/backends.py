# app/memory/backends.py
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime, timedelta
import redis
import json
from app.memory.schema import ShortTermMemoryEntry


class STMBackend(ABC):
    @abstractmethod
    def set(self, session_id: str, key: str, entry: ShortTermMemoryEntry):
        pass

    @abstractmethod
    def get(self, session_id: str, key: str) -> Optional[ShortTermMemoryEntry]:
        pass

    @abstractmethod
    def get_all(self, session_id: str) -> Dict[str, ShortTermMemoryEntry]:
        pass

    @abstractmethod
    def clear(self, session_id: str):
        pass

    @abstractmethod
    def cleanup_expired(self):
        pass


class InMemorySTMBackend(STMBackend):
    def __init__(self, ttl_minutes: int = 30):
        self._store: Dict[str, Dict[str, ShortTermMemoryEntry]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def set(self, session_id: str, key: str, entry: ShortTermMemoryEntry):
        self._store.setdefault(session_id, {})[key] = entry

    def get(self, session_id: str, key: str) -> Optional[ShortTermMemoryEntry]:
        session_data = self._store.get(session_id, {})
        entry = session_data.get(key)
        if entry and not self._is_expired(entry.timestamp):
            return entry
        return None

    def get_all(self, session_id: str) -> Dict[str, ShortTermMemoryEntry]:
        session_data = self._store.get(session_id, {})
        return {
            k: v for k, v in session_data.items() if not self._is_expired(v.timestamp)
        }

    def clear(self, session_id: str):
        if session_id in self._store:
            del self._store[session_id]

    def cleanup_expired(self):
        expired_keys = []
        for session_id, session_data in self._store.items():
            expired_session_keys = [
                key
                for key, entry in session_data.items()
                if self._is_expired(entry.timestamp)
            ]
            for key in expired_session_keys:
                del session_data[key]
            if not session_data:
                expired_keys.append(session_id)

        for key in expired_keys:
            del self._store[key]

    def _is_expired(self, timestamp: datetime) -> bool:
        return datetime.now(timestamp.tzinfo) - timestamp > self.ttl


class RedisSTMBackend(STMBackend):
    def __init__(
        self, redis_url: str = "redis://localhost:6379", ttl_minutes: int = 30
    ):
        self.redis_client = redis.from_url(redis_url)
        self.ttl_seconds = ttl_minutes * 60

    def _key(self, session_id: str, key: str = None) -> str:
        if key:
            return f"stm:{session_id}:{key}"
        return f"stm:{session_id}:*"

    def set(self, session_id: str, key: str, entry: ShortTermMemoryEntry):
        redis_key = self._key(session_id, key)
        data = entry.model_dump_json()
        self.redis_client.setex(redis_key, self.ttl_seconds, data)

    def get(self, session_id: str, key: str) -> Optional[ShortTermMemoryEntry]:
        redis_key = self._key(session_id, key)
        data = self.redis_client.get(redis_key)
        if data:
            return ShortTermMemoryEntry.model_validate_json(data)
        return None

    def get_all(self, session_id: str) -> Dict[str, ShortTermMemoryEntry]:
        pattern = self._key(session_id).replace("*", "*")
        keys = self.redis_client.keys(pattern)
        result = {}

        for redis_key in keys:
            data = self.redis_client.get(redis_key)
            if data:
                entry = ShortTermMemoryEntry.model_validate_json(data)
                key = redis_key.decode().split(":")[-1]
                result[key] = entry

        return result

    def clear(self, session_id: str):
        pattern = self._key(session_id).replace("*", "*")
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)

    def cleanup_expired(self):
        # Redis handles TTL automatically, so this is a no-op
        pass
