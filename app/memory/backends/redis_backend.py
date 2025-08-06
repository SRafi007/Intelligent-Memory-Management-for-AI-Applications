# app/memory/backends/redis_backend.py
import redis
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import settings


class RedisSTMBackend:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(
            host=host, port=port, db=db, decode_responses=True
        )
        self.ttl_seconds = settings.STM_TTL_MINUTES * 60

    def set(self, session_id: str, key: str, value: str):
        redis_key = f"stm:{session_id}:{key}"
        entry = {"value": value, "timestamp": datetime.utcnow().isoformat()}
        self.redis_client.setex(redis_key, self.ttl_seconds, json.dumps(entry))

    def get(self, session_id: str, key: str) -> str:
        redis_key = f"stm:{session_id}:{key}"
        data = self.redis_client.get(redis_key)
        if data:
            entry = json.loads(data)
            return entry["value"]
        return ""

    def get_all(self, session_id: str) -> Dict[str, str]:
        pattern = f"stm:{session_id}:*"
        keys = self.redis_client.keys(pattern)
        result = {}
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                entry = json.loads(data)
                clean_key = key.split(":")[-1]  # Extract original key
                result[clean_key] = entry["value"]
        return result
