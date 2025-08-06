# app/config/settings.py

# Long Term Memory settings
LTM_COLLECTION_NAME = "memory_management_long_term_memory"
LTM_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LTM_VECTOR_SIZE = 384
LTM_QDRANT_HOST = "localhost"
LTM_QDRANT_PORT = 6333

# Short Term Memory settings
STM_TTL_MINUTES = 30

# ADD new settings (optional - with defaults)
USE_REDIS_STM = False  # Default to your current in-memory system
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

EMBEDDING_PROVIDER = "sentence_transformer"  # or "openai"
OPENAI_API_KEY = None  # Only needed if using OpenAI embeddings

# Plugin settings
ENABLE_ENTITY_EXTRACTION = False
ENABLE_SENTIMENT_ANALYSIS = False
