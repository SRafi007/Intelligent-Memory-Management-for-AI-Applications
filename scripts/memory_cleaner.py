# scripts/memory_cleaner.py
#!/usr/bin/env python3
"""
Script to clean memory data from both STM and LTM
"""

import argparse
import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.memory.memory_manager import MemoryManager
from qdrant_client import QdrantClient
from app.config.settings import *


def clear_stm(memory_manager: MemoryManager, session_id: Optional[str] = None):
    """Clear Short Term Memory data"""
    if session_id:
        print(f"Clearing STM for session: {session_id}")
        memory_manager.clear_short_term(session_id)
        print("STM session cleared.")
    else:
        print("Warning: Cannot clear all STM sessions with current implementation.")
        print("Please specify --session-id to clear a specific session.")


def clear_ltm(collection_name: str, user_id: Optional[str] = None):
    """Clear Long Term Memory data"""
    client = QdrantClient(host=LTM_QDRANT_HOST, port=LTM_QDRANT_PORT)

    try:
        if not client.collection_exists(collection_name):
            print(f"Collection '{collection_name}' does not exist.")
            return

        if user_id:
            print(f"Clearing LTM for user: {user_id}")
            # Delete points with specific user_id
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(key="user_id", match=MatchValue(value=user_id))
                    ]
                ),
            )
            print(f"LTM data for user '{user_id}' cleared.")
        else:
            print(f"Clearing entire LTM collection: {collection_name}")
            response = input(
                "Are you sure? This will delete ALL memory data! (yes/no): "
            )
            if response.lower() == "yes":
                client.delete_collection(collection_name)
                print("Entire LTM collection deleted.")
            else:
                print("Operation cancelled.")

    except Exception as e:
        print(f"Error clearing LTM: {e}")


def cleanup_expired_stm(memory_manager: MemoryManager):
    """Cleanup expired STM entries"""
    print("Cleaning up expired STM entries...")
    memory_manager.stm.cleanup_expired()
    print("Expired STM entries cleaned up.")


def main():
    parser = argparse.ArgumentParser(description="Clean memory system data")
    parser.add_argument(
        "--backend", choices=["memory", "redis"], default="memory", help="STM backend"
    )
    parser.add_argument(
        "--redis-url", default="redis://localhost:6379", help="Redis URL"
    )
    parser.add_argument(
        "--clear",
        choices=["stm", "ltm", "both", "expired"],
        required=True,
        help="What to clear",
    )
    parser.add_argument("--session-id", help="Session ID for STM clearing")
    parser.add_argument("--user-id", help="User ID for LTM clearing")
    parser.add_argument(
        "--collection", default=LTM_COLLECTION_NAME, help="LTM collection name"
    )

    args = parser.parse_args()

    # Initialize memory manager
    memory_manager = MemoryManager(
        stm_backend=args.backend,
        redis_url=args.redis_url,
        collection_name=args.collection,
    )

    if args.clear in ["stm", "both"]:
        clear_stm(memory_manager, args.session_id)

    if args.clear in ["ltm", "both"]:
        clear_ltm(args.collection, args.user_id)

    if args.clear == "expired":
        cleanup_expired_stm(memory_manager)


if __name__ == "__main__":
    main()
