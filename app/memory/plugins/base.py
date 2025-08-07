# app/memory/plugins/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MemoryPlugin(ABC):
    @abstractmethod
    def process_before_storage(self, text: str, metadata: Dict) -> tuple[str, Dict]:
        """Process data before storing in memory"""
        pass

    @abstractmethod
    def process_before_retrieval(self, query: str, results: List) -> List:
        """Process results before returning"""
        pass
