"""# app/integrations/langchain_integration.py
from langchain.schema import BaseMemory
from typing import Any, Dict, List


class LangChainMemoryAdapter(BaseMemory):
    def __init__(self, memory_manager, user_id: str, session_id: str):
        self.memory_manager = memory_manager
        self.user_id = user_id
        self.session_id = session_id

    @property
    def memory_variables(self) -> List[str]:
        return ["history", "context"]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Get recent conversation context
        context = self.memory_manager.recall(
            user_id=self.user_id,
            query=inputs.get("input", ""),
            session_id=self.session_id,
            top_k=5,
        )

        history = "\n".join([entry.text for entry in context])

        return {"history": history, "context": context}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        # Save the interaction to memory
        user_input = inputs.get("input", "")
        ai_output = outputs.get("output", "")

        # Store in STM for immediate context
        self.memory_manager.set_short_term(
            self.session_id,
            f"interaction_{datetime.utcnow().timestamp()}",
            f"Human: {user_input}\nAI: {ai_output}",
        )

        # Optionally promote to LTM based on importance
        combined_text = f"User: {user_input}\nAssistant: {ai_output}"
        importance = score_importance(combined_text)

        if importance > 0.3:
            self.memory_manager.add_long_term(
                user_id=self.user_id,
                text=combined_text,
                metadata={"type": "conversation", "session_id": self.session_id},
            )

    def clear(self) -> None:
        self.memory_manager.clear_short_term(self.session_id)



# app/integrations/llamaindex_integration.py
from llama_index.core.memory import BaseMemory
from typing import List, Optional

class LlamaIndexMemoryAdapter(BaseMemory):
    def __init__(self, memory_manager, user_id: str):
        self.memory_manager = memory_manager
        self.user_id = user_id

    def get_all(self) -> List[str]:
        # Get all relevant memories for this user
        memories = self.memory_manager.search_long_term(
            query="",  # Empty query to get all
            user_id=self.user_id,
            top_k=100
        )
        return [memory.text for memory in memories]

    def get(self, **kwargs) -> List[str]:
        query = kwargs.get("query", "")
        memories = self.memory_manager.search_long_term(
            query=query,
            user_id=self.user_id,
            top_k=kwargs.get("top_k", 5)
        )
        return [memory.text for memory in memories]

    def put(self, text: str, **kwargs) -> None:
        self.memory_manager.add_long_term(
            user_id=self.user_id,
            text=text,
            metadata=kwargs
        )

"""
