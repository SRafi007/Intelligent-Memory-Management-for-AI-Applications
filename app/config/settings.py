# app/config/settings.py

# Long Term Memory settings
LTM_COLLECTION_NAME = "memory_management_long_term_memory"
LTM_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LTM_VECTOR_SIZE = 384
LTM_QDRANT_HOST = "localhost"
LTM_QDRANT_PORT = 6333

# Short Term Memory settings
STM_TTL_MINUTES = 30
# Redis settings
USE_REDIS_STM = False  # Set to True to use Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Embedding settings
EMBEDDING_PROVIDER = "sentence_transformer"  # Only sentence_transformer for now

# Lifecycle settings
MEMORY_CLEANUP_DAYS = 90
IMPORTANCE_THRESHOLD_FOR_CLEANUP = 0.3
SIMILARITY_THRESHOLD_FOR_CONSOLIDATION = 0.95

# Search settings
DEFAULT_SEARCH_TYPE = "hybrid"
MAX_SEARCH_RESULTS = 100
