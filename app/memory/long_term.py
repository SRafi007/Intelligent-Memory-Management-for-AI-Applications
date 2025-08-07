# app/memory/long_term.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer
from app.memory.schema import LongTermMemoryEntry
from app.config import settings  # ✅ import config
from uuid import uuid4
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LongTermMemory:
    def __init__(
        self,
        host: str = settings.LTM_QDRANT_HOST,
        port: int = settings.LTM_QDRANT_PORT,
        collection_name: str = settings.LTM_COLLECTION_NAME,
        embedding_model: str = settings.LTM_EMBEDDING_MODEL,
        vector_size: int = settings.LTM_VECTOR_SIZE,
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer(embedding_model)
        self._ensure_collection(vector_size)

    def _ensure_collection(self, vector_size: int):
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def add_entry(
        self,
        user_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> Optional[str]:
        #  deduplication with metadata consideration
        search_filters = {"user_id": user_id}
        if conversation_id:
            search_filters["conversation_id"] = conversation_id

        existing = self.search(query_text=text, top_k=3, filters=search_filters)

        for e in existing:
            # More sophisticated similarity check
            if self._texts_similar(e.text, text, threshold=0.95):
                logger.info(f"Similar entry found. Skipping: {text[:50]}...")
                return None

        # Add with conversation context
        embedding = self.model.encode(text).tolist()
        entry_id = str(uuid4())
        metadata = metadata or {}
        if conversation_id:
            metadata["conversation_id"] = conversation_id

        point = PointStruct(
            id=entry_id,
            vector=embedding,
            payload={"user_id": user_id, "text": text, "metadata": metadata},
        )

        self.client.upsert(collection_name=self.collection_name, points=[point])
        return entry_id

    def search(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.3,
    ) -> List[LongTermMemoryEntry]:
        query_vector = self.model.encode(query_text).tolist()

        # Build Qdrant filter
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == "user_id":
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                else:
                    conditions.append(
                        FieldCondition(
                            key=f"metadata.{key}", match=MatchValue(value=value)
                        )
                    )

            if conditions:
                qdrant_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            score_threshold=min_score,
        )

        memory_entries = []
        for result in results:
            payload = result.payload
            memory_entries.append(
                LongTermMemoryEntry(
                    id=str(result.id),
                    user_id=payload["user_id"],
                    text=payload["text"],
                    metadata=payload.get("metadata", {}),
                    embedding=result.vector,
                )
            )

        return memory_entries

    def _texts_similar(self, text1: str, text2: str, threshold: float = 0.95) -> bool:
        """Simple text similarity check"""
        text1_clean = text1.strip().lower()
        text2_clean = text2.strip().lower()

        if text1_clean == text2_clean:
            return True

        # Simple Jaccard similarity for words
        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())

        if not words1 or not words2:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union >= threshold

    def summarize_old_memories(self, user_id: str, days_old: int = 30) -> Optional[str]:
        """Basic memory summarization to prevent growth"""
        # This is a placeholder for more sophisticated summarization
        # Could use LLM to summarize old conversations
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days_old)
        # Implementation would filter by date and summarize
        # For now, just return None
        return None
