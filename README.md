# AI Memory Building Blocks

A **plug-and-play memory system** designed to store, recall, and score contextual memory — usable in **chatbots**, **agents**, **task systems**, or **LLM pipelines**.

## Features

* **Short-Term Memory (STM)**: Stores session-level data with TTL.
* **Long-Term Memory (LTM)**: Stores vectorized memory using Qdrant.
* **Deduplication**: Prevents storing duplicate thoughts.
* **Importance Scoring**: Tags memory based on urgency/keywords.
* **Visualization**: View top important memories graphically.
* **Unit-Tested**: Includes tests for STM, LTM, and promotions.

## Data Flow

```
┌───────────────────┐
│ Your AI Agent     │
└────────┬──────────┘
         │
┌─────────▼──────────┐
│ ShortTermMemory    │
│ (session, TTL)     │
└─────────┬──────────┘
         │ Promote STM
         ▼
┌─────────▼──────────┐
│ LongTermMemory     │
│ (Qdrant vector DB) │
└─────────┬──────────┘
         │
┌──────────▼──────────┐
│ MemoryManager API   │
└──────────┬──────────┘
         │
┌────────────▼─────────────┐
│ Scoring + Deduplication  │
└──────────────────────────┘
```

## File Structure Overview

```
ai-memory-building-blocks/
├── app/
│   ├── config/
│   │   └── settings.py           # All memory configs
│   └── memory/
│       ├── schema.py             # Memory entry models
│       ├── scoring.py            # Importance scoring logic
│       ├── short_term.py         # STM engine (in-memory with TTL)
│       ├── long_term.py          # LTM engine (Qdrant-backed)
│       └── memory_manager.py     # Unified interface for STM+LTM
├── examples/
│   ├── memory_demo.py            # Shows usage of STM + LTM
│   ├── clear_ltm.py              # Delete Qdrant collection
│   └── visualize_top_memories.py # Plot important memories
├── scripts/
│   ├── export_ltm.py             # Export LTM to JSON
│   ├── import_ltm.py             # Import LTM from JSON
│   └── view_ltm.py               # View all entries
├── tests/
│   └── test_memory.py            # Unit tests for STM, LTM, promotion
├── requirements.txt
├── README.md                     # ← You're here
└── SETUP.md                      # Setup & integration guide
```

## Quick Demo

```bash
# Run Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Run memory demo
python examples/memory_demo.py

# Visualize important memories
python examples/visualize_top_memories.py

# Run tests
pytest tests/
```

## Integrating Into Your Project

To plug this into your AI/LLM/Agent app:

1. Copy:
   * `app/memory/`
   * `app/config/settings.py`
2. Set up Qdrant (local or remote)
3. Use:

```python
from app.memory.memory_manager import MemoryManager

memory = MemoryManager()
memory.set_short_term("session1", "intent", "book_flight")
memory.promote_stm_to_ltm("session1", "user_123")
results = memory.recall("user_123", "flight")
```

See full instructions in `SETUP.md`

## Use Cases

* **Chatbots & Agents** – Remember past conversations
* **Task AI** – Recall user preferences, scheduled meetings
* **LLM Chains** – Feed memory context to prompts
* **RAG Systems** – Store/retrieve vectorized memory

## Persistence

* STM is stored in RAM (clears after TTL or shutdown)
* LTM is persisted in **Qdrant**, a blazing-fast vector DB
  * Optionally export/import from JSON

## Future Additions

* Replace `search()` with `query_points()` (Qdrant)
* Convert to installable pip package
* Add FastAPI / REST wrapper
* Add AI-powered scoring (using OpenAI or LLM)

## Author

Made with by Sadman Sakib Rafi