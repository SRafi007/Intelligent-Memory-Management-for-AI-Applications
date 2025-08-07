# app/memory/lifecycle.py
"""
Memory lifecycle management for preventing infinite growth
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.memory.schema import MemoryEntry
import logging

logger = logging.getLogger(__name__)


class MemoryLifecycleManager:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def archive_old_memories(
        self, user_id: str, days_threshold: int = 90, importance_threshold: float = 0.3
    ) -> Dict[str, int]:
        """Archive or delete old, unimportant memories"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

        # Get old memories (this is a placeholder - you'd need to implement date filtering)
        old_memories = self._get_memories_before_date(user_id, cutoff_date)

        deleted_count = 0
        summarized_count = 0

        for memory in old_memories:
            if memory.importance < importance_threshold:
                # Delete low-importance old memories
                if self._delete_memory(memory.id):
                    deleted_count += 1
            else:
                # Summarize and compress important old memories
                if self._summarize_memory(memory):
                    summarized_count += 1

        logger.info(
            f"Lifecycle cleanup: {deleted_count} deleted, {summarized_count} summarized"
        )
        return {"deleted": deleted_count, "summarized": summarized_count}

    def consolidate_similar_memories(
        self, user_id: str, similarity_threshold: float = 0.95
    ) -> int:
        """Merge very similar memories to reduce duplication"""
        # Get all memories for user
        all_memories = self.memory_manager.search_long_term(
            query="", user_id=user_id, top_k=1000  # Empty query to get all
        )

        consolidated_count = 0
        processed_ids = set()

        for i, memory1 in enumerate(all_memories):
            if memory1.id in processed_ids:
                continue

            similar_memories = []

            # Find similar memories
            for j, memory2 in enumerate(all_memories[i + 1 :], i + 1):
                if memory2.id in processed_ids:
                    continue

                # Calculate similarity (this is a simple approach)
                similarity = self._calculate_similarity(memory1.text, memory2.text)

                if similarity >= similarity_threshold:
                    similar_memories.append(memory2)

            # Consolidate if we found similar memories
            if similar_memories:
                consolidated_text = self._merge_memories([memory1] + similar_memories)

                # Create consolidated memory
                self.memory_manager.add_long_term(
                    user_id=user_id,
                    text=consolidated_text,
                    metadata={
                        **memory1.metadata,
                        "consolidated_from": [
                            m.id for m in [memory1] + similar_memories
                        ],
                        "consolidated_at": datetime.utcnow().isoformat(),
                    },
                )

                # Mark for deletion
                for memory in [memory1] + similar_memories:
                    processed_ids.add(memory.id)
                    self._delete_memory(memory.id)

                consolidated_count += len(similar_memories) + 1

        logger.info(f"Consolidated {consolidated_count} similar memories")
        return consolidated_count

    def cleanup_expired_stm(self):
        """Clean up expired STM entries (if using in-memory STM)"""
        # This would clean up expired entries from in-memory STM
        # Redis STM handles expiration automatically
        if hasattr(self.memory_manager.stm, "_store"):
            # Implementation for in-memory cleanup
            pass

    def _get_memories_before_date(
        self, user_id: str, cutoff_date: datetime
    ) -> List[MemoryEntry]:
        """Get memories older than cutoff date"""
        # This is a placeholder - you'd need to implement date filtering in your search
        all_memories = self.memory_manager.search_long_term(
            query="", user_id=user_id, top_k=1000
        )

        return [memory for memory in all_memories if memory.timestamp < cutoff_date]

    def _delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        # You'd need to implement deletion in your LTM class
        # This is a placeholder
        try:
            # self.memory_manager.ltm.delete_entry(memory_id)
            logger.info(f"Would delete memory {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def _summarize_memory(self, memory: MemoryEntry) -> bool:
        """Create a compressed version of the memory"""
        try:
            # Simple summarization - could use LLM for better results
            summary = f"Summary: {memory.text[:100]}..."

            self.memory_manager.add_long_term(
                user_id=memory.user_id,
                text=summary,
                metadata={
                    **memory.metadata,
                    "original_id": memory.id,
                    "is_summary": True,
                    "original_timestamp": memory.timestamp.isoformat(),
                    "summarized_at": datetime.utcnow().isoformat(),
                },
            )

            # Delete original
            return self._delete_memory(memory.id)

        except Exception as e:
            logger.error(f"Failed to summarize memory {memory.id}: {e}")
            return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple approach - you could use embeddings for better results
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _merge_memories(self, memories: List[MemoryEntry]) -> str:
        """Merge multiple similar memories into one"""
        # Simple approach - could be improved
        texts = [memory.text for memory in memories]
        return f"Consolidated memory: {' | '.join(texts)}"
