# tests/test_memory.py

import pytest
from app.memory.memory_manager import MemoryManager
from app.memory.schema import MemoryEntry


@pytest.fixture
def memory():
    return MemoryManager()


def test_stm_set_and_get(memory):
    session_id = "test_session"
    memory.set_short_term(session_id, "task", "Test short term memory")
    result = memory.get_short_term(session_id, "task")
    assert result == "Test short term memory"


def test_stm_clear(memory):
    session_id = "test_session"
    memory.set_short_term(session_id, "task", "to be cleared")
    memory.clear_short_term(session_id)
    assert memory.get_short_term(session_id, "task") == ""


def test_ltm_add_and_recall(memory):
    user_id = "test_user"
    text = "This is a test long term memory entry"
    memory.add_long_term(user_id=user_id, text=text, metadata={"source": "unit_test"})
    results = memory.recall(user_id=user_id, query="test long", top_k=3)
    assert any("test long term memory entry" in r.text for r in results)


def test_stm_to_ltm_promotion(memory):
    session_id = "promote_session"
    user_id = "user_promote"

    memory.set_short_term(session_id, "reminder", "Urgent! Meeting at 10AM. ASAP")
    ltm_id = memory.promote_stm_to_ltm(session_id=session_id, user_id=user_id)

    assert ltm_id is not None

    # Verify recall from LTM
    results = memory.recall(user_id=user_id, query="meeting")
    assert any("meeting" in r.text.lower() for r in results)
