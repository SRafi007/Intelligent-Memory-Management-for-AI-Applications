"""
Comprehensive test script for the enhanced memory system
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add your app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_enhanced_memory_system():
    """Test all components of the enhanced memory system"""

    print("🧪 Testing Enhanced Memory System")
    print("=" * 50)

    # Import your enhanced components

    from app.memory.memory_manager import MemoryManager
    from app.memory.conversation import ConversationMemory
    from app.memory.search import AdvancedSearch, SearchType, SearchFilter
    from app.memory.lifecycle import MemoryLifecycleManager

    # Test 1: Basic Memory Manager (your existing functionality)
    print("\n1. Testing Basic Memory Manager...")
    try:
        # Test with in-memory STM (your current system)
        memory_manager = MemoryManager(use_redis=False)

        # Test STM
        memory_manager.set_short_term("test_session", "user_name", "John Doe")
        retrieved = memory_manager.get_short_term("test_session", "user_name")
        assert retrieved == "John Doe", f"Expected 'John Doe', got '{retrieved}'"

        # Test LTM
        ltm_id = memory_manager.add_long_term(
            user_id="test_user",
            text="I love pizza and Italian food in general",
            metadata={"category": "preferences"},
        )

        # Search LTM
        results = memory_manager.search_long_term(
            query="food preferences", user_id="test_user"
        )

        assert len(results) > 0, "No results found in LTM search"
        print(f"✅ Basic memory manager working - found {len(results)} results")

    except Exception as e:
        print(f"❌ Basic memory manager test failed: {e}")
        return

    # Test 2: Redis STM (if available)
    print("\n2. Testing Redis STM...")
    try:
        memory_manager_redis = MemoryManager(use_redis=True)
        memory_manager_redis.set_short_term("redis_session", "test_key", "redis_value")
        redis_result = memory_manager_redis.get_short_term("redis_session", "test_key")
        assert redis_result == "redis_value", f"Redis test failed: {redis_result}"
        print("✅ Redis STM working")
    except Exception as e:
        print(f"⚠️ Redis STM not available or failed: {e}")
        # Continue with in-memory STM
        memory_manager = MemoryManager(use_redis=False)

    # Test 3: Conversation Memory
    print("\n3. Testing Conversation Memory...")
    try:
        conv_memory = ConversationMemory(memory_manager)

        # Add conversation turns
        conv_memory.add_conversation_turn(
            user_id="test_user",
            session_id="conv_session",
            user_message="What's the weather like?",
            assistant_message="I don't have access to current weather data, but I can help you find weather information.",
            context={"topic": "weather"},
        )

        conv_memory.add_conversation_turn(
            user_id="test_user",
            session_id="conv_session",
            user_message="Can you help me plan a trip to Paris?",
            assistant_message="I'd be happy to help you plan a trip to Paris! What specific aspects would you like help with?",
            context={"topic": "travel"},
        )

        # Get conversation context
        context = conv_memory.get_conversation_context("conv_session", last_n_turns=2)
        assert len(context) == 2, f"Expected 2 conversation turns, got {len(context)}"

        # Get relevant history
        relevant_history = conv_memory.get_relevant_history(
            "test_user", "travel planning"
        )
        print(
            f"✅ Conversation memory working - {len(context)} turns stored, {len(relevant_history)} relevant memories"
        )

    except Exception as e:
        print(f"❌ Conversation memory test failed: {e}")
        return

    # Test 4: Advanced Search
    print("\n4. Testing Advanced Search...")
    try:
        search = AdvancedSearch(memory_manager)

        # Add more memories for better search testing
        memory_manager.add_long_term(
            "test_user", "I work as a software engineer", {"category": "work"}
        )
        memory_manager.add_long_term(
            "test_user",
            "My favorite programming language is Python",
            {"category": "work"},
        )
        memory_manager.add_long_term(
            "test_user", "I enjoy hiking on weekends", {"category": "hobbies"}
        )

        # Test different search types
        semantic_results = search.search("programming", SearchType.SEMANTIC, top_k=3)
        keyword_results = search.search(
            "Python programming", SearchType.KEYWORD, top_k=3
        )
        hybrid_results = search.search(
            "software development", SearchType.HYBRID, top_k=3
        )

        # Test with filters
        work_filter = SearchFilter(metadata_filters={"category": "work"})
        filtered_results = search.search(
            "engineer", SearchType.SEMANTIC, filters=work_filter, top_k=5
        )

        print(f"✅ Advanced search working:")
        print(f"   - Semantic: {len(semantic_results)} results")
        print(f"   - Keyword: {len(keyword_results)} results")
        print(f"   - Hybrid: {len(hybrid_results)} results")
        print(f"   - Filtered: {len(filtered_results)} results")

    except Exception as e:
        print(f"❌ Advanced search test failed: {e}")
        return

    # Test 5: Memory Lifecycle
    print("\n5. Testing Memory Lifecycle...")
    try:
        lifecycle = MemoryLifecycleManager(memory_manager)

        # Add some test memories
        for i in range(5):
            memory_manager.add_long_term(
                user_id="test_user",
                text=f"Test memory {i} with low importance",
                metadata={"test": True},
                importance=0.1,  # Low importance
            )

        # Test archiving (this is mostly placeholder functionality)
        archive_results = lifecycle.archive_old_memories(
            user_id="test_user",
            days_threshold=0,  # Archive immediately for testing
            importance_threshold=0.3,
        )

        # Test consolidation
        consolidation_count = lifecycle.consolidate_similar_memories("test_user")

        print(f"✅ Memory lifecycle working:")
        print(f"   - Archive results: {archive_results}")
        print(f"   - Consolidation count: {consolidation_count}")

    except Exception as e:
        print(f"❌ Memory lifecycle test failed: {e}")
        return

    # Test 6: Integration Test
    print("\n6. Running Integration Test...")
    try:
        # Simulate a real conversation flow
        user_id = "integration_test_user"
        session_id = "integration_session"

        # User asks about favorite foods
        conv_memory.add_conversation_turn(
            user_id=user_id,
            session_id=session_id,
            user_message="What should I cook for dinner?",
            assistant_message="What type of cuisine do you enjoy?",
            context={"topic": "cooking"},
        )

        # User mentions preference
        memory_manager.add_long_term(
            user_id=user_id,
            text="User likes spicy Thai food and vegetarian dishes",
            metadata={"type": "preference", "category": "food"},
        )

        # Later conversation - search for relevant context
        food_memories = search.search(
            "cooking dinner",
            SearchType.HYBRID,
            filters=SearchFilter(user_id=user_id),
            top_k=3,
        )

        conversation_context = conv_memory.get_conversation_context(session_id)

        print(f"✅ Integration test successful:")
        print(f"   - Found {len(food_memories)} relevant food memories")
        print(f"   - Retrieved {len(conversation_context)} conversation turns")

        # Display some results
        if food_memories:
            print(f"   - Sample memory: {food_memories[0].text[:50]}...")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return

    print("\n🎉 All tests completed successfully!")
    print("\nNext steps:")
    print("1. Set USE_REDIS_STM = True in settings.py if you have Redis running")
    print("2. Customize the importance scoring in scoring.py for your use case")
    print("3. Add more sophisticated plugins for entity extraction, etc.")
    print("4. Integrate with your AI application using the conversation memory")


if __name__ == "__main__":
    test_enhanced_memory_system()
