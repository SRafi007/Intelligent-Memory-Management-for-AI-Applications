# tests/test_stm.py

import time
from app.memory.short_term import ShortTermMemory
from app.memory.backends import InMemorySTMBackend


def test_set_and_get_stm_entry():
    backend = InMemorySTMBackend(ttl_minutes=1)
    stm = ShortTermMemory(backend)

    stm.set("session123", "greeting", "Hello world")
    result = stm.get("session123", "greeting")

    assert result == "Hello world"


def test_get_all_returns_all_non_expired_entries():
    backend = InMemorySTMBackend(ttl_minutes=1)
    stm = ShortTermMemory(backend)

    stm.set("session123", "k1", "v1")
    stm.set("session123", "k2", "v2")

    result = stm.get_all("session123")

    assert result == {"k1": "v1", "k2": "v2"}


def test_clear_removes_session_entries():
    backend = InMemorySTMBackend(ttl_minutes=1)
    stm = ShortTermMemory(backend)

    stm.set("session123", "k1", "v1")
    stm.clear("session123")

    result = stm.get("session123", "k1")
    assert result == ""


def test_expired_entries_are_removed_on_get():
    backend = InMemorySTMBackend(ttl_minutes=0.01)  # 0.6 seconds
    stm = ShortTermMemory(backend)

    stm.set("session123", "temp", "soon gone")
    time.sleep(1)

    result = stm.get("session123", "temp")
    assert result == ""
