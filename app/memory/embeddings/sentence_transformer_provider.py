# app/memory/embeddings/sentence_transformer_provider.py
"""
Sentence Transformer embedding provider (your current approach)
"""
from sentence_transformers import SentenceTransformer
from .base import EmbeddingProvider
from typing import List


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def encode(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
