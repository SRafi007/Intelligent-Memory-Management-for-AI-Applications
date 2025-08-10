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
├── tests/
│   └── test_memory.py            # Unit tests for STM, LTM, promotion
├── requirements.txt
├── README.md                     # ← You're here
└── SETUP.md                      # Setup & integration guide
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