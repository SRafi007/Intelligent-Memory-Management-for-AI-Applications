# app/memory/embeddings/base.py
"""
Abstract embedding provider interface
"""
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass
