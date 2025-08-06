# app/memory/plugins/entity_extractor.py
import spacy
from .base import MemoryPlugin
from typing import Any, Dict, List


class EntityExtractionPlugin(MemoryPlugin):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def process_before_storage(self, text: str, metadata: Dict) -> tuple[str, Dict]:
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        metadata["entities"] = entities
        metadata["has_person"] = any(label == "PERSON" for _, label in entities)
        metadata["has_org"] = any(label == "ORG" for _, label in entities)

        return text, metadata

    def process_before_retrieval(self, query: str, results: List) -> List:
        # Could boost results that mention entities from the query
        return results
