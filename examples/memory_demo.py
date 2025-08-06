# examples/memory_demo.py

from app.memory.memory_manager import MemoryManager

memory = MemoryManager()

# Step 1: Simulate STM usage
session_id = "session_abc"
user_id = "user_123"

memory.set_short_term(session_id, "intent", "add_task")
memory.set_short_term(session_id, "task", "Call Sarah at 4 PM")
memory.set_short_term(session_id, "date", "2025-08-06")

print("\n🟢 Short-Term Memory:")
print(memory.get_all_short_term(session_id))

# Step 2: Promote STM to LTM
ltm_id = memory.promote_stm_to_ltm(session_id, user_id)
print(f"\n🟦 Promoted to LTM with ID: {ltm_id}")

# Step 3: Search in LTM
query = "What tasks do I have with Sarah?"
results = memory.search_long_term(query, user_id=user_id)

print("\n🔍 LTM Search Results:")
for r in results:
    print(f"- [{r.timestamp}] {r.text}")
