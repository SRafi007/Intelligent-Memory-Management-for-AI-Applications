# app/config/settings.py
from typing import Literal

# Memory Backend Configuration
STM_BACKEND: Literal["memory", "redis"] = "memory"
REDIS_URL = "redis://localhost:6379"

# Long Term Memory settings
LTM_COLLECTION_NAME = "memory_management_long_term_memory"
LTM_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LTM_VECTOR_SIZE = 384
LTM_QDRANT_HOST = "localhost"
LTM_QDRANT_PORT = 6333

# Short Term Memory settings
STM_TTL_MINUTES = 30

# Cleanup settings
ENABLE_CLEANUP = True
CLEANUP_INTERVAL_MINUTES = 60

# Search settings
MIN_SEARCH_SCORE = 0.3
