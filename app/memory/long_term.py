# app/memory/long_term.py

from typing import Optional, Dict, Any, List
import logging
from app.memory.backends import QdrantLTMBackend, LTMBackend
from app.memory.schema import LongTermMemoryEntry
from app.config.settings import settings
import json
from pathlib import Path


class LongTermMemory:
    ...

    def export_json(self, filepath: str):
        """Export all LTM entries to JSON."""
        # This assumes backend can return all stored entries
        # For Qdrant, we need to scroll through points
        all_entries = self.backend.export_all()
        Path(filepath).write_text(
            json.dumps([e.model_dump() for e in all_entries], default=str, indent=2)
        )

    def import_json(self, filepath: str):
        """Import LTM entries from JSON."""
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(filepath)
        entries = json.loads(file_path.read_text())
        for entry_dict in entries:
            entry = LongTermMemoryEntry(**entry_dict)
            self.backend.add_entry(
                user_id=entry.user_id,
                text=entry.text,
                metadata=entry.metadata,
                conversation_id=entry.metadata.get("conversation_id"),
            )


logger = logging.getLogger(__name__)


class LongTermMemory:
    """
    A wrapper around an LTM backend (default: Qdrant) that adds:
    - Deduplication before insertion
    - Optional conversation-aware filtering
    """

    def __init__(
        self,
        backend: Optional[LTMBackend] = None,
        host: str = settings.LTM_QDRANT_HOST,
        port: int = settings.LTM_QDRANT_PORT,
        collection_name: str = settings.LTM_COLLECTION_NAME,
        embedding_model: str = settings.LTM_EMBEDDING_MODEL,
        vector_size: int = settings.LTM_VECTOR_SIZE,
    ):
        # Use provided backend or default to Qdrant
        self.backend = backend or QdrantLTMBackend(
            host=host,
            port=port,
            collection_name=collection_name,
            embedding_model=embedding_model,
            vector_size=vector_size,
        )

    def add_entry(
        self,
        user_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> Optional[str]:
        # Deduplication
        search_filters = {"user_id": user_id}
        if conversation_id:
            search_filters["conversation_id"] = conversation_id

        existing_entries = self.search(query_text=text, top_k=3, filters=search_filters)
        for e in existing_entries:
            if self._texts_similar(e.text, text, threshold=0.95):
                logger.info(f"Similar entry found. Skipping: {text[:50]}...")
                return None

        return self.backend.add_entry(user_id, text, metadata, conversation_id)

    def search(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = settings.MIN_SEARCH_SCORE,
    ) -> List[LongTermMemoryEntry]:
        return self.backend.search(
            query_text, top_k=top_k, filters=filters, min_score=min_score
        )

    def _texts_similar(self, text1: str, text2: str, threshold: float = 0.95) -> bool:
        """Basic text similarity check using Jaccard similarity."""
        text1_clean = text1.strip().lower()
        text2_clean = text2.strip().lower()

        if text1_clean == text2_clean:
            return True

        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())

        if not words1 or not words2:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union >= threshold

    def summarize_old_memories(self, user_id: str, days_old: int = 30) -> Optional[str]:
        """Placeholder for summarizing old memories."""
        return None

    def export_json(self, filepath: str):
        """Export all LTM entries to JSON."""
        # This assumes backend can return all stored entries
        # For Qdrant, we need to scroll through points
        all_entries = self.backend.export_all()
        Path(filepath).write_text(
            json.dumps([e.model_dump() for e in all_entries], default=str, indent=2)
        )

    def import_json(self, filepath: str):
        """Import LTM entries from JSON."""
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(filepath)
        entries = json.loads(file_path.read_text())
        for entry_dict in entries:
            entry = LongTermMemoryEntry(**entry_dict)
            self.backend.add_entry(
                user_id=entry.user_id,
                text=entry.text,
                metadata=entry.metadata,
                conversation_id=entry.metadata.get("conversation_id"),
            )
