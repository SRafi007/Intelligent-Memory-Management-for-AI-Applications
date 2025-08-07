# test_memory_system.py
import time
import json
from datetime import datetime
from typing import Dict, Any

# Import our enhanced memory system
from app.memory.memory_manager import MemoryManager
from app.memory.backends import InMemorySTMBackend, RedisSTMBackend


class MemorySystemTester:
    def __init__(self):
        self.test_results = {}
        self.current_test = ""

    def log(self, message: str, data: Any = None):
        """Enhanced logging to see what's happening"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {self.current_test}: {message}")
        if data:
            if isinstance(data, (dict, list)):
                print(f"    Data: {json.dumps(data, indent=2, default=str)}")
            else:
                print(f"    Data: {data}")
        print("-" * 50)

    def verify_redis_connection(self):
        """Test Redis connection and show what's in Redis"""
        self.current_test = "REDIS_CONNECTION"
        try:
            import redis

            r = redis.from_url("redis://localhost:6379")
            r.ping()
            self.log("✅ Redis connection successful")

            # Show all keys in Redis
            all_keys = r.keys("*")
            self.log(f"Current Redis keys", [key.decode() for key in all_keys])
            return True
        except Exception as e:
            self.log(f"❌ Redis connection failed: {e}")
            return False

    def verify_qdrant_connection(self):
        """Test Qdrant connection and show collections"""
        self.current_test = "QDRANT_CONNECTION"
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(host="localhost", port=6333)

            # List all collections
            collections = client.get_collections()
            self.log("✅ Qdrant connection successful")
            self.log("Current collections", [c.name for c in collections.collections])
            return True
        except Exception as e:
            self.log(f"❌ Qdrant connection failed: {e}")
            return False

    def test_stm_in_memory(self):
        """Test in-memory STM backend"""
        self.current_test = "STM_IN_MEMORY"

        memory = MemoryManager(stm_backend="memory")

        # Test basic operations
        self.log("Setting STM values")
        memory.set_short_term("session1", "user_name", "Alice")
        memory.set_short_term("session1", "preference", "likes coffee")
        memory.set_short_term("session2", "user_name", "Bob")

        # Retrieve and verify
        alice_name = memory.get_short_term("session1", "user_name")
        alice_pref = memory.get_short_term("session1", "preference")
        bob_name = memory.get_short_term("session2", "user_name")

        self.log(
            "Retrieved STM values",
            {
                "session1_user_name": alice_name,
                "session1_preference": alice_pref,
                "session2_user_name": bob_name,
            },
        )

        # Get all from session
        all_session1 = memory.get_all_short_term("session1")
        self.log("All session1 data", all_session1)

        return memory

    def test_stm_redis(self):
        """Test Redis STM backend"""
        self.current_test = "STM_REDIS"

        if not self.verify_redis_connection():
            self.log("Skipping Redis STM test - no connection")
            return None

        memory = MemoryManager(stm_backend="redis")

        # Clear any existing test data
        import redis

        r = redis.from_url("redis://localhost:6379")
        test_keys = r.keys("stm:test_session*")
        if test_keys:
            r.delete(*test_keys)
            self.log("Cleared existing test data from Redis")

        # Test operations
        self.log("Setting Redis STM values")
        memory.set_short_term("test_session1", "user_name", "Charlie")
        memory.set_short_term("test_session1", "mood", "happy")
        memory.set_short_term("test_session2", "user_name", "Diana")

        # Check Redis directly
        redis_keys_after = [key.decode() for key in r.keys("stm:test_session*")]
        self.log("Redis keys created", redis_keys_after)

        # Check TTL on keys
        for key in redis_keys_after:
            ttl = r.ttl(key)
            self.log(f"TTL for {key}: {ttl} seconds")

        # Retrieve through memory manager
        charlie_name = memory.get_short_term("test_session1", "user_name")
        charlie_mood = memory.get_short_term("test_session1", "mood")
        diana_name = memory.get_short_term("test_session2", "user_name")

        self.log(
            "Retrieved Redis STM values",
            {
                "test_session1_user_name": charlie_name,
                "test_session1_mood": charlie_mood,
                "test_session2_user_name": diana_name,
            },
        )

        # Get all from session
        all_test_session1 = memory.get_all_short_term("test_session1")
        self.log("All test_session1 data", all_test_session1)

        return memory

    def test_ltm_operations(self, memory: MemoryManager):
        """Test Long Term Memory operations"""
        self.current_test = "LTM_OPERATIONS"

        # Add various types of memories
        memories_to_add = [
            {
                "user_id": "user123",
                "text": "User prefers morning meetings and dislikes afternoon calls",
                "conversation_id": "conv_001",
                "context": {"user_explicitly_asked_to_remember": True},
            },
            {
                "user_id": "user123",
                "text": "Emergency contact: John Doe at 555-1234",
                "conversation_id": "conv_002",
                "context": {"conversation_length": 15},
            },
            {
                "user_id": "user456",
                "text": "Prefers email over phone calls",
                "conversation_id": "conv_003",
            },
            {
                "user_id": "user123",
                "text": "Birthday is March 15th, loves chocolate cake",
                "conversation_id": "conv_001",
            },
        ]

        added_ids = []
        for i, memory_data in enumerate(memories_to_add):
            self.log(f"Adding memory {i+1}", memory_data)
            memory_id = memory.add_long_term(**memory_data)
            added_ids.append(memory_id)
            self.log(f"Memory added with ID: {memory_id}")

        # Check Qdrant directly
        from qdrant_client import QdrantClient

        client = QdrantClient(host="localhost", port=6333)
        collection_info = client.get_collection("ai_memory_project_long_term_memory")
        self.log(
            "Qdrant collection info",
            {
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
            },
        )

        # Test searching
        self.log("Testing LTM searches")

        # Basic search
        search1 = memory.search_long_term("meetings", user_id="user123")
        self.log(
            "Search 'meetings' for user123",
            [
                {"text": r.text[:50] + "...", "importance": r.importance}
                for r in search1
            ],
        )

        # Search with conversation filter
        search2 = memory.search_long_term(
            "preferences", user_id="user123", filters={"conversation_id": "conv_001"}
        )
        self.log(
            "Search 'preferences' in conv_001",
            [
                {
                    "text": r.text[:50] + "...",
                    "conversation": r.metadata.get("conversation_id"),
                }
                for r in search2
            ],
        )

        # Cross-user search (should return nothing due to user filter)
        search3 = memory.search_long_term("email", user_id="user123")
        self.log(
            "Search 'email' for user123 (should be empty)", [r.text for r in search3]
        )

        # Search without user filter
        search4 = memory.search_long_term("email", top_k=10, min_score=0.1)
        self.log(
            "Search 'email' all users",
            [{"user": r.user_id, "text": r.text[:30] + "..."} for r in search4],
        )

        return added_ids

    def test_recall_functionality(self, memory: MemoryManager):
        """Test the recall function that combines STM and LTM"""
        self.current_test = "RECALL_FUNCTIONALITY"

        # Add some STM data
        memory.set_short_term(
            "current_session", "current_topic", "We're discussing meeting preferences"
        )
        memory.set_short_term(
            "current_session", "user_mood", "User seems frustrated with scheduling"
        )

        # Test recall - should check STM first, then LTM
        self.log("Testing recall for 'meeting'")
        recall_results = memory.recall(
            user_id="user123",
            query="meeting",
            session_id="current_session",
            conversation_id="conv_001",
            top_k=3,
        )

        self.log(
            "Recall results",
            [
                {
                    "source": r.source,
                    "text": r.text[:50] + "...",
                    "importance": r.importance,
                }
                for r in recall_results
            ],
        )

        # Test recall without STM session
        self.log("Testing recall without STM session")
        recall_results2 = memory.recall(user_id="user123", query="birthday", top_k=2)

        self.log(
            "Recall results (LTM only)",
            [
                {
                    "source": r.source,
                    "text": r.text[:50] + "...",
                }
                for r in recall_results2
            ],
        )

    def test_stm_to_ltm_promotion(self, memory: MemoryManager):
        """Test promoting STM to LTM"""
        self.current_test = "STM_TO_LTM_PROMOTION"

        # Create a session with important information
        session_id = "important_session"
        memory.set_short_term(
            session_id, "task", "URGENT: Call client about contract deadline"
        )
        memory.set_short_term(session_id, "deadline", "Must complete by Friday")
        memory.set_short_term(
            session_id, "contact", "Client: Sarah Johnson, sarah@company.com"
        )

        self.log("STM data before promotion", memory.get_all_short_term(session_id))

        # Promote to LTM
        promoted_id = memory.promote_stm_to_ltm(
            session_id=session_id,
            user_id="user123",
            conversation_id="urgent_conv",
            min_importance=0.2,  # Lower threshold to ensure promotion
        )

        self.log(f"Promoted to LTM with ID: {promoted_id}")
        self.log("STM data after promotion", memory.get_all_short_term(session_id))

        # Verify it's in LTM
        if promoted_id:
            ltm_search = memory.search_long_term("urgent client", user_id="user123")
            self.log(
                "LTM search for promoted content",
                [
                    {"text": r.text[:80] + "...", "importance": r.importance}
                    for r in ltm_search
                ],
            )

    def test_cleanup_functionality(self):
        """Test the cleanup functionality"""
        self.current_test = "CLEANUP_FUNCTIONALITY"

        # Test with very short TTL
        memory = MemoryManager(
            stm_backend="memory",
            stm_ttl_minutes=0.01,  # 0.6 seconds
            enable_cleanup=False,  # Manual cleanup for testing
        )

        # Add some data
        memory.set_short_term("temp_session", "temp_key", "This will expire soon")
        self.log("Added temporary data")

        # Verify it exists
        temp_data = memory.get_short_term("temp_session", "temp_key")
        self.log(f"Data exists: {temp_data}")

        # Wait for expiration
        self.log("Waiting for data to expire...")
        time.sleep(2)

        # Try to get expired data
        expired_data = memory.get_short_term("temp_session", "temp_key")
        self.log(f"Data after expiration: '{expired_data}' (should be empty)")

        # Manual cleanup
        memory.stm.cleanup_expired()
        self.log("Manual cleanup completed")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("STARTING COMPREHENSIVE MEMORY SYSTEM TESTS")
        print("=" * 60)

        # Connection tests
        redis_available = self.verify_redis_connection()
        qdrant_available = self.verify_qdrant_connection()

        if not qdrant_available:
            print("❌ Cannot proceed without Qdrant")
            return

        # STM Tests
        print("\n" + "=" * 40)
        print("TESTING SHORT TERM MEMORY")
        print("=" * 40)

        memory_in_mem = self.test_stm_in_memory()

        if redis_available:
            memory_redis = self.test_stm_redis()
            memory = memory_redis  # Use Redis version for remaining tests
        else:
            memory = memory_in_mem  # Fallback to in-memory

        # LTM Tests
        print("\n" + "=" * 40)
        print("TESTING LONG TERM MEMORY")
        print("=" * 40)

        added_ids = self.test_ltm_operations(memory)

        # Integration Tests
        print("\n" + "=" * 40)
        print("TESTING INTEGRATION FEATURES")
        print("=" * 40)

        self.test_recall_functionality(memory)
        self.test_stm_to_ltm_promotion(memory)
        self.test_cleanup_functionality()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)

        # Final state check
        self.current_test = "FINAL_STATE"
        self.log(
            "Final Redis keys",
            self._get_redis_keys() if redis_available else "Redis not available",
        )
        self.log(
            "Final Qdrant collections",
            (
                self._get_qdrant_collections()
                if qdrant_available
                else "Qdrant not available"
            ),
        )

    def _get_redis_keys(self):
        """Helper to get current Redis keys"""
        try:
            import redis

            r = redis.from_url("redis://localhost:6379")
            return [key.decode() for key in r.keys("*")]
        except:
            return []

    def _get_qdrant_collections(self):
        """Helper to get current Qdrant collections"""
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(host="localhost", port=6333)
            collections = client.get_collections()
            return [c.name for c in collections.collections]
        except:
            return []


def test_specific_scenario():
    """Test a specific real-world scenario"""
    print("\n" + "=" * 60)
    print("TESTING REAL-WORLD SCENARIO: AI ASSISTANT CONVERSATION")
    print("=" * 60)

    memory = MemoryManager(stm_backend="redis")

    # Simulate a conversation about project planning
    session_id = "project_planning_session"
    user_id = "john_doe"
    conversation_id = "project_alpha"

    print("🎬 Scenario: User is planning a project with AI assistant")
    print()

    # Short-term context during conversation
    memory.set_short_term(
        session_id, "current_project", "Project Alpha - Mobile App Development"
    )
    memory.set_short_term(session_id, "team_size", "5 developers, 2 designers, 1 PM")
    memory.set_short_term(session_id, "timeline", "6 months")
    memory.set_short_term(
        session_id,
        "budget_constraint",
        "Limited budget - need cost-effective solutions",
    )

    print("📝 Added conversation context to STM:")
    stm_data = memory.get_all_short_term(session_id)
    for key, value in stm_data.items():
        print(f"   {key}: {value}")

    # Important information that should be remembered long-term
    important_memories = [
        "User prefers React Native for cross-platform development",
        "Team has experience with Firebase but new to AWS",
        "Previous project had issues with performance optimization",
        "Client requires offline functionality for the mobile app",
        "User is concerned about app store approval process",
    ]

    print("\n💾 Adding important information to LTM:")
    for memory_text in important_memories:
        memory_id = memory.add_long_term(
            user_id=user_id,
            text=memory_text,
            conversation_id=conversation_id,
            context={"conversation_length": len(important_memories)},
        )
        print(f"   ✅ Added: {memory_text[:50]}... (ID: {memory_id[:8]})")

    # Later in conversation - test recall
    print("\n🔍 Later in conversation - testing intelligent recall:")

    queries = [
        "What technology should we use?",
        "What problems did we have before?",
        "What does the client need?",
        "team experience",
    ]

    for query in queries:
        print(f"\n   Query: '{query}'")
        results = memory.recall(
            user_id=user_id,
            query=query,
            session_id=session_id,
            conversation_id=conversation_id,
            top_k=2,
        )

        for i, result in enumerate(results, 1):
            source_emoji = "🧠" if result.source == "short_term" else "📚"
            importance = f"(importance: {result.importance:.2f})"
            print(f"      {source_emoji} {i}. {result.text[:60]}... {importance}")

    # End of conversation - promote STM to LTM
    print(f"\n⬆️  End of conversation - promoting STM to LTM:")
    promoted_id = memory.promote_stm_to_ltm(
        session_id=session_id,
        user_id=user_id,
        conversation_id=conversation_id,
        min_importance=0.2,
    )

    if promoted_id:
        print(f"   ✅ Successfully promoted STM content (ID: {promoted_id[:8]})")
    else:
        print("   ℹ️  STM content didn't meet importance threshold for promotion")

    print(f"\n📊 Final memory state:")
    print(f"   STM entries: {len(memory.get_all_short_term(session_id))}")

    ltm_results = memory.search_long_term("project", user_id=user_id, top_k=10)
    print(f"   LTM entries for user: {len(ltm_results)}")


if __name__ == "__main__":
    # Run comprehensive tests
    tester = MemorySystemTester()
    tester.run_all_tests()

    # Run specific scenario
    test_specific_scenario()
