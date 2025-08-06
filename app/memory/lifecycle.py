# app/memory/lifecycle.py
from typing import List, Optional
from datetime import datetime, timedelta
from app.memory.schema import MemoryEntry


class MemoryLifecycleManager:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def archive_old_memories(
        self, user_id: str, days_threshold: int = 90, importance_threshold: float = 0.3
    ):
        """Archive or delete old, unimportant memories"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

        # Query old memories
        old_memories = self._get_memories_before_date(user_id, cutoff_date)

        for memory in old_memories:
            if memory.importance < importance_threshold:
                # Delete low-importance old memories
                self._delete_memory(memory.id)
            else:
                # Summarize and compress important old memories
                self._summarize_memory(memory)

    def consolidate_similar_memories(
        self, user_id: str, similarity_threshold: float = 0.9
    ):
        """Merge very similar memories to reduce duplication"""
        # Implementation for finding and merging similar memories
        pass

    def _summarize_memory(self, memory: MemoryEntry):
        """Create a compressed version of the memory"""
        # Could use LLM to create summary
        summary = f"Summary: {memory.text[:100]}..."  # Simple truncation

        self.memory_manager.add_long_term(
            user_id=memory.user_id,
            text=summary,
            metadata={
                **memory.metadata,
                "original_id": memory.id,
                "is_summary": True,
                "original_timestamp": memory.timestamp.isoformat(),
            },
        )

        # Delete original
        self._delete_memory(memory.id)
