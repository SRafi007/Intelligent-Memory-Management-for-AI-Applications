# Test that your existing code still works:
from app.memory.memory_manager import MemoryManager

# This should work exactly as before
memory_manager = MemoryManager()

# Test new Redis capability (optional)
memory_manager_redis = MemoryManager(use_redis=True)

# Test new embedding providers (optional)
memory_manager_embedding = MemoryManager(embedding_model="all-MiniLM-L6-v2")

# Test with plugins (optional)
from app.memory.plugins.entity_extractor import EntityExtractionPlugin

memory_manager_plugins = MemoryManager(plugins=[EntityExtractionPlugin()])
