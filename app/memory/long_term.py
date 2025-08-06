# app/memory/long_term.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, SearchRequest

# from sentence_transformers import SentenceTransformer
from app.memory.schema import LongTermMemoryEntry
from uuid import uuid4
from typing import List, Optional
import logging
from app.memory.embeddings.sentence_transformer_provider import (
    SentenceTransformerProvider,
)


from app.config import settings  # <-- Import settings

logger = logging.getLogger(__name__)


class LongTermMemory:
    def __init__(
        self,
        host: str = settings.LTM_QDRANT_HOST,
        port: int = settings.LTM_QDRANT_PORT,
        collection_name: str = settings.LTM_COLLECTION_NAME,
        embedding_model: str = settings.LTM_EMBEDDING_MODEL,
        vector_size: int = settings.LTM_VECTOR_SIZE,
        embedding_provider: str = "sentence_transformer",  # ADD this parameter
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)

        # REPLACE this line:
        # self.model = SentenceTransformer(embedding_model)
        self.embedding_provider = SentenceTransformerProvider(
            model_name=embedding_model
        )
        vector_size = self.embedding_provider.dimension
        """
        # WITH this logic:
        if embedding_provider == "openai":
            self.embedding_provider = OpenAIEmbeddingProvider(model=embedding_model)
            vector_size = self.embedding_provider.dimension
        else:
            self.embedding_provider = SentenceTransformerProvider(model_name=embedding_model)
            vector_size = self.embedding_provider.dimension

        """

        self._ensure_collection(vector_size)

    def _ensure_collection(self, vector_size: int):
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def add_entry(
        self, user_id: str, text: str, metadata: Optional[dict] = None
    ) -> Optional[str]:
        # Deduplication: search for similar text
        existing = self.search(query_text=text, top_k=3, user_id=user_id)
        for e in existing:
            if e.text.strip().lower() == text.strip().lower():
                logger.info(f"Duplicate entry found. Skipping: {text}")
                return None  # Don't re-save duplicate

        # Proceed with adding
        embedding = self.embedding_provider.encode(text)
        entry_id = str(uuid4())
        metadata = metadata or {}

        point = PointStruct(
            id=entry_id,
            vector=embedding,
            payload={"user_id": user_id, "text": text, "metadata": metadata},
        )

        self.client.upsert(collection_name=self.collection_name, points=[point])
        return entry_id

    def search(
        self, query_text: str, top_k: int = 5, user_id: Optional[str] = None
    ) -> List[LongTermMemoryEntry]:
        query_vector = self.embedding_provider.encode(query_text)

        results = self.client.search(
            collection_name=self.collection_name, query_vector=query_vector, limit=top_k
        )

        memory_entries = []
        for result in results:
            payload = result.payload
            if user_id and payload.get("user_id") != user_id:
                continue

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
