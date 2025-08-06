# app/memory/embeddings/sentence_transformer_provider.py
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


"""

# app/memory/embeddings/openai_provider.py
import openai
from .base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        self.model = model
        self.client = openai.Client(api_key=api_key)

    def encode(self, text: str) -> List[float]:
        response = self.client.embeddings.create(input=text, model=self.model)
        return response.data[0].embedding

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        return 1536 if "3-large" in self.model else 512


"""
