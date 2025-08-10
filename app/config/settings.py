# app/config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

from typing import Literal


class Settings(BaseSettings):
    # Memory Backend
    STM_BACKEND: Literal["memory", "redis"] = "redis"
    REDIS_URL: str = "redis://localhost:6379"

    # Long-Term Memory
    LTM_COLLECTION_NAME: str = "memory_management_long_term_memory"
    LTM_VECTOR_SIZE: int = 384
    LTM_QDRANT_HOST: str = "localhost"
    LTM_QDRANT_PORT: int = 6333
    LTM_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    # LTM_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    # LTM_EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
    DEDUPLICATION_THRESHOLD: float = 0.92
    LTM_SUMMARIZATION_DAYS: int = 30  # Age threshold
    LTM_PRUNE_AFTER_SUMMARY: bool = True
    # Summarization & pruning
    LTM_SUMMARIZATION_PROVIDER: str = "none"  # "openai" | "ollama" | "none"
    LTM_SUMMARIZATION_MODEL: str = "gpt-4o-mini"  # provider-specific
    LTM_SUMMARIZATION_DAYS: int = 30
    LTM_PRUNE_AFTER_SUMMARY: bool = True

    # Short-Term Memory
    STM_TTL_MINUTES: int = 30

    # Cleanup
    ENABLE_CLEANUP: bool = True
    CLEANUP_INTERVAL_MINUTES: int = 60

    # Search
    MIN_SEARCH_SCORE: float = 0.3

    model_config = {"env_file": ".env"}


settings = Settings()
