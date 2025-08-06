# app/memory/conversation.py
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel
import json
from datetime import datetime


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
        # Store in STM for immediate context
        conversation_context = {
            "last_user_message": user_message,
            "last_assistant_message": assistant_message,
            "turn_timestamp": datetime.utcnow().isoformat(),
        }

        self.memory_manager.set_short_term(
            session_id,
            f"conversation_turn_{datetime.utcnow().timestamp()}",
            json.dumps(conversation_context),
        )

        # Determine if this turn is important enough for LTM
        combined_turn = f"User: {user_message}\nAssistant: {assistant_message}"
        importance = self.memory_manager.ltm.model.encode(
            combined_turn
        )  # Custom scoring

        if importance > 0.3:  # Configurable threshold
            self.memory_manager.add_long_term(
                user_id=user_id,
                text=combined_turn,
                metadata={
                    "type": "conversation_turn",
                    "session_id": session_id,
                    "context": context or {},
                },
            )

    def get_conversation_context(self, session_id: str, last_n_turns: int = 5) -> str:
        """Get recent conversation context for AI model"""
        stm_data = self.memory_manager.get_all_short_term(session_id)
        conversation_turns = [
            v for k, v in stm_data.items() if k.startswith("conversation_turn_")
        ]

        # Sort by timestamp and get last N
        sorted_turns = sorted(conversation_turns, key=lambda x: x)[-last_n_turns:]
        return "\n".join(sorted_turns)
