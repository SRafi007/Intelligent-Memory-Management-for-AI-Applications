# app/memory/search/search.py
"""
Advanced search capabilities with hybrid search
"""

from typing import List, Optional, Dict, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import re
from app.memory.schema import MemoryEntry


class SearchType(Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    METADATA = "metadata"


@dataclass
class SearchFilter:
    user_id: Optional[str] = None
    date_range: Optional[tuple] = None
    importance_min: Optional[float] = None
    importance_max: Optional[float] = None
    metadata_filters: Optional[Dict] = None
    source: Optional[str] = None  # 'short_term', 'long_term', or None for both
    memory_type: Optional[str] = None  # Filter by memory type


class AdvancedSearch:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def search(
        self,
        query: str,
        search_type: SearchType = SearchType.HYBRID,
        filters: Optional[SearchFilter] = None,
        top_k: int = 5,
    ) -> List[MemoryEntry]:
        """Main search interface"""

        filters = filters or SearchFilter()

        if search_type == SearchType.SEMANTIC:
            return self._semantic_search(query, filters, top_k)
        elif search_type == SearchType.KEYWORD:
            return self._keyword_search(query, filters, top_k)
        elif search_type == SearchType.HYBRID:
            return self._hybrid_search(query, filters, top_k)
        else:
            return self._metadata_search(query, filters, top_k)

    def _semantic_search(
        self, query: str, filters: SearchFilter, top_k: int
    ) -> List[MemoryEntry]:
        """Vector-based semantic search"""
        # Use existing LTM search (your current implementation)
        results = self.memory_manager.search_long_term(
            query=query,
            user_id=filters.user_id,
            top_k=top_k * 2,  # Get more results for filtering
        )
        return self._apply_filters(results, filters)[:top_k]

    def _keyword_search(
        self, query: str, filters: SearchFilter, top_k: int
    ) -> List[MemoryEntry]:
        """Simple keyword-based search"""
        results = []
        query_words = query.lower().split()

        # Search STM if not filtered out
        if filters.source != "long_term":
            stm_results = self._search_stm_keywords(query_words, filters)
            results.extend(stm_results)

        # Search LTM if not filtered out
        if filters.source != "short_term":
            ltm_results = self._search_ltm_keywords(query_words, filters)
            results.extend(ltm_results)

        # Simple scoring by number of keyword matches
        def keyword_score(entry):
            text_words = entry.text.lower().split()
            matches = sum(
                1
                for word in query_words
                if any(word in text_word for text_word in text_words)
            )
            return matches / len(query_words) if query_words else 0

        results.sort(key=keyword_score, reverse=True)
        return results[:top_k]

    def _hybrid_search(
        self, query: str, filters: SearchFilter, top_k: int
    ) -> List[MemoryEntry]:
        """Combine semantic and keyword search with weighted scoring"""
        # Get results from both approaches
        semantic_results = self._semantic_search(query, filters, top_k * 2)
        keyword_results = self._keyword_search(query, filters, top_k * 2)

        # Combine and deduplicate
        combined_results = {}

        # Add semantic results with weight
        for i, result in enumerate(semantic_results):
            key = result.text  # Use text as key for deduplication
            semantic_score = (
                (len(semantic_results) - i) / len(semantic_results)
                if semantic_results
                else 0
            )
            combined_results[key] = {
                "entry": result,
                "semantic_score": semantic_score * 0.7,  # 70% weight
                "keyword_score": 0,
            }

        # Add keyword results with weight
        for i, result in enumerate(keyword_results):
            key = result.text
            keyword_score = (
                (len(keyword_results) - i) / len(keyword_results)
                if keyword_results
                else 0
            )

            if key in combined_results:
                combined_results[key]["keyword_score"] = (
                    keyword_score * 0.3
                )  # 30% weight
            else:
                combined_results[key] = {
                    "entry": result,
                    "semantic_score": 0,
                    "keyword_score": keyword_score * 0.3,
                }

        # Calculate final scores and sort
        final_results = []
        for key, data in combined_results.items():
            final_score = data["semantic_score"] + data["keyword_score"]
            entry = data["entry"]
            # You could store the score in metadata if needed
            entry.metadata["search_score"] = final_score
            final_results.append(entry)

        final_results.sort(
            key=lambda x: x.metadata.get("search_score", 0), reverse=True
        )
        return final_results[:top_k]

    def _search_stm_keywords(
        self, query_words: List[str], filters: SearchFilter
    ) -> List[MemoryEntry]:
        """Search STM for keywords"""
        results = []
        # Implementation depends on having access to all STM sessions
        # For now, this is a simplified version
        return results

    def _search_ltm_keywords(
        self, query_words: List[str], filters: SearchFilter
    ) -> List[MemoryEntry]:
        """Search LTM for keywords - this would need to be implemented in your LTM class"""
        # This is a placeholder - you'd need to add keyword search to your LTM
        return []

    def _metadata_search(
        self, query: str, filters: SearchFilter, top_k: int
    ) -> List[MemoryEntry]:
        """Search based on metadata criteria"""
        # Get all memories and filter by metadata
        all_memories = self.memory_manager.search_long_term(
            query="",  # Empty query to get all
            user_id=filters.user_id,
            top_k=1000,  # Get many results for filtering
        )

        filtered_results = self._apply_filters(all_memories, filters)
        return filtered_results[:top_k]

    def _apply_filters(
        self, results: List[MemoryEntry], filters: SearchFilter
    ) -> List[MemoryEntry]:
        """Apply various filters to search results"""
        filtered_results = results

        # Filter by importance range
        if filters.importance_min is not None:
            filtered_results = [
                r for r in filtered_results if r.importance >= filters.importance_min
            ]

        if filters.importance_max is not None:
            filtered_results = [
                r for r in filtered_results if r.importance <= filters.importance_max
            ]

        # Filter by memory type
        if filters.memory_type:
            filtered_results = [
                r
                for r in filtered_results
                if r.metadata.get("type") == filters.memory_type
            ]

        # Filter by date range
        if filters.date_range:
            start_date, end_date = filters.date_range
            filtered_results = [
                r for r in filtered_results if start_date <= r.timestamp <= end_date
            ]

        # Filter by custom metadata
        if filters.metadata_filters:
            for key, value in filters.metadata_filters.items():
                filtered_results = [
                    r for r in filtered_results if r.metadata.get(key) == value
                ]

        return filtered_results
