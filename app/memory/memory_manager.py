# app/memory/memory_manager.py

# This file defines the MemoryManager class, which orchestrates
# both short-term and long-term memory for an application.

# Import necessary types and modules.
from typing import Optional, Dict, List
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.schema import MemoryEntry
from app.memory.scoring import score_importance
from app.config import settings
from datetime import datetime

from app.memory.plugins.base import MemoryPlugin


class MemoryManager:
    # Initializes the manager with instances of short-term and long-term memory.
    def __init__(
        self,
        stm_ttl_minutes: int = settings.STM_TTL_MINUTES,
        collection_name: str = settings.LTM_COLLECTION_NAME,
        embedding_model: str = settings.LTM_EMBEDDING_MODEL,
        use_redis: bool = False,  # ADD this parameter
        plugins: List[MemoryPlugin] = None,  # ADD this parameter
    ):
        self.stm = ShortTermMemory(ttl_minutes=stm_ttl_minutes, use_redis=use_redis)

        self.ltm = LongTermMemory(
            collection_name=collection_name, embedding_model=embedding_model
        )

        # ADD plugin support
        self.plugins = plugins or []

    # Stores a key-value pair in short-term memory for a given session.
    def set_short_term(self, session_id: str, key: str, value: str):
        self.stm.set(session_id, key, value)

    # Retrieves a value from short-term memory using a key and session ID.
    def get_short_term(self, session_id: str, key: str) -> str:
        return self.stm.get(session_id, key)

    # Retrieves all key-value pairs from a specific session's short-term memory.
    def get_all_short_term(self, session_id: str) -> Dict[str, str]:
        return self.stm.get_all(session_id)

    # Deletes all data associated with a specific session from short-term memory.
    def clear_short_term(self, session_id: str):
        self.stm.clear(session_id)

    # ========== LTM (Long-Term Memory) ==========
    # These methods handle permanent memory storage and retrieval.

    # Adds a new entry to long-term memory.
    # It automatically scores the importance of the text if not provided.
    def add_long_term(
        self,
        user_id: str,
        text: str,
        metadata: Optional[dict] = None,
        importance: Optional[float] = None,
    ) -> Optional[str]:
        metadata = metadata or {}

        # ADD plugin processing
        processed_text, processed_metadata = text, metadata
        for plugin in self.plugins:
            processed_text, processed_metadata = plugin.process_before_storage(
                processed_text, processed_metadata
            )

        # Your existing logic continues with processed data
        if importance is None:
            importance = score_importance(processed_text)
        processed_metadata["importance"] = importance

        return self.ltm.add_entry(
            user_id=user_id, text=processed_text, metadata=processed_metadata
        )

    # Searches long-term memory for entries related to a given query.
    # It returns a list of the most relevant entries.
    def search_long_term(
        self, query: str, user_id: Optional[str] = None, top_k: int = 5
    ) -> List[MemoryEntry]:
        ltm_results = self.ltm.search(query_text=query, user_id=user_id, top_k=top_k)
        return [
            MemoryEntry(
                id=entry.id,
                user_id=entry.user_id,
                text=entry.text,
                metadata=entry.metadata,
                timestamp=entry.timestamp,
                source="long_term",
                importance=entry.metadata.get("importance", 0.5),
            )
            for entry in ltm_results
        ]

    # ========== Recall ==========
    # This method is the primary way to retrieve memory, combining both STM and LTM.

    # Recalls relevant memories by first checking short-term memory (STM).
    # If a sufficient number of results are not found in STM, it falls back to
    # searching long-term memory (LTM) to get the best matches.
    def recall(
        self, user_id: str, query: str, session_id: Optional[str] = None, top_k: int = 5
    ) -> List[MemoryEntry]:
        stm_entries: List[MemoryEntry] = []

        if session_id:
            stm_data = self.stm.get_all(session_id)
            for key, value in stm_data.items():
                if query.lower() in value.lower():
                    stm_entries.append(
                        MemoryEntry(
                            id=None,
                            user_id=user_id,
                            text=value,
                            metadata={"key": key},
                            timestamp=datetime.now(),
                            source="short_term",
                            importance=0.5,
                        )
                    )
            if len(stm_entries) >= top_k:
                return stm_entries[:top_k]

        # Fallback to LTM if STM doesn't have enough results.
        ltm_entries = self.search_long_term(query=query, user_id=user_id, top_k=top_k)
        # Combines STM and LTM results, removing any duplicates from LTM.
        combined = stm_entries + [
            e for e in ltm_entries if e.text not in {x.text for x in stm_entries}
        ]
        return combined[:top_k]

    # ========== STM → LTM Promotion ==========
    # This method provides a mechanism to move important short-term data to long-term memory.

    # Promotes the contents of a short-term memory session to long-term memory.
    # It first scores the importance of the combined STM data.
    # If the score meets a minimum threshold, it adds the data to LTM and then clears STM.
    def promote_stm_to_ltm(
        self, session_id: str, user_id: str, min_importance: float = 0.3
    ) -> Optional[str]:
        stm_data = self.stm.get_all(session_id)
        if not stm_data:
            return None

        combined_text = "\n".join([f"{k}: {v}" for k, v in stm_data.items()])
        score = score_importance(combined_text)

        if score >= min_importance:
            ltm_id = self.add_long_term(
                user_id=user_id,
                text=combined_text,
                metadata={"source": "stm_promotion"},
                importance=score,
            )
            self.clear_short_term(session_id)
            return ltm_id

        return None
