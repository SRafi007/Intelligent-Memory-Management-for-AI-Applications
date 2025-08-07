# app/memory/conversation.py
"""
Conversation-aware memory management
"""
import json
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from app.memory.scoring import score_importance


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Dict = {}


class ConversationMemory:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def add_conversation_turn(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        assistant_message: str,
        context: Optional[Dict] = None,
    ):
        """Store a complete conversation turn"""
        # Store in STM for immediate context
        conversation_context = {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
        }

        turn_key = f"conv_turn_{int(datetime.utcnow().timestamp())}"
        self.memory_manager.set_short_term(
            session_id, turn_key, json.dumps(conversation_context)
        )

        # Determine if this turn should go to LTM
        combined_turn = f"User: {user_message}\nAssistant: {assistant_message}"
        importance = score_importance(combined_turn)

        if importance > 0.2:  # Lower threshold for conversations
            self.memory_manager.add_long_term(
                user_id=user_id,
                text=combined_turn,
                metadata={
                    "type": "conversation_turn",
                    "session_id": session_id,
                    "importance": importance,
                    "context": context or {},
                },
                importance=importance,
            )

    def get_conversation_context(
        self, session_id: str, last_n_turns: int = 5
    ) -> List[Dict]:
        """Get recent conversation context for AI model"""
        stm_data = self.memory_manager.get_all_short_term(session_id)
        conversation_turns = []

        for key, value in stm_data.items():
            if key.startswith("conv_turn_"):
                try:
                    turn_data = json.loads(value)
                    conversation_turns.append(
                        {
                            "timestamp": turn_data["timestamp"],
                            "user": turn_data["user_message"],
                            "assistant": turn_data["assistant_message"],
                            "context": turn_data.get("context", {}),
                        }
                    )
                except json.JSONDecodeError:
                    continue

        # Sort by timestamp and get last N
        conversation_turns.sort(key=lambda x: x["timestamp"])
        return conversation_turns[-last_n_turns:]

    def get_relevant_history(
        self, user_id: str, current_query: str, top_k: int = 3
    ) -> List[str]:
        """Get relevant conversation history from LTM"""
        relevant_memories = self.memory_manager.search_long_term(
            query=current_query, user_id=user_id, top_k=top_k
        )

        # Filter for conversation turns
        conversation_memories = [
            memory.text
            for memory in relevant_memories
            if memory.metadata.get("type") == "conversation_turn"
        ]

        return conversation_memories
