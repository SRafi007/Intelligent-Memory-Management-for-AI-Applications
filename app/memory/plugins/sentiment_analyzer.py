# app/memory/plugins/sentiment_analyzer.py
from textblob import TextBlob
from .base import MemoryPlugin
from typing import Any, Dict, List


class SentimentPlugin(MemoryPlugin):
    def process_before_storage(self, text: str, metadata: Dict) -> tuple[str, Dict]:
        blob = TextBlob(text)
        metadata["sentiment"] = {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
        }
        return text, metadata

    def process_before_retrieval(self, query: str, results: List) -> List:
        return results
