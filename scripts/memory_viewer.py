# scripts/memory_viewer.py
#!/usr/bin/env python3
"""
Simple script to view memory data from both STM and LTM
"""

import argparse
import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.memory.memory_manager import MemoryManager
from app.config.settings import *


def view_stm(memory_manager: MemoryManager, session_id: str):
    """View Short Term Memory data"""
    print(f"\n=== Short Term Memory (Session: {session_id}) ===")
    stm_data = memory_manager.get_all_short_term(session_id)

    if not stm_data:
        print("No STM data found for this session.")
        return

    for key, value in stm_data.items():
        print(f"Key: {key}")
        print(f"Value: {value}")
        print("-" * 50)


def view_ltm(
    memory_manager: MemoryManager,
    user_id: Optional[str] = None,
    query: str = "*",
    limit: int = 10,
):
    """View Long Term Memory data"""
    print(f"\n=== Long Term Memory ===")
    print(f"User ID: {user_id or 'All users'}")
    print(f"Query: {query}")
    print(f"Limit: {limit}")
    print("-" * 50)

    if query == "*":
        # For viewing all, we'll use a broad search
        query = "conversation meeting task note"

    try:
        results = memory_manager.search_long_term(
            query=query,
            user_id=user_id,
            top_k=limit,
            min_score=0.0,  # Lower threshold to see more results
        )

        if not results:
            print("No LTM data found.")
            return

        for i, entry in enumerate(results, 1):
            print(f"{i}. ID: {entry.id}")
            print(f"   User: {entry.user_id}")
            print(
                f"   Text: {entry.text[:100]}{'...' if len(entry.text) > 100 else ''}"
            )
            print(f"   Importance: {entry.importance:.3f}")
            print(f"   Timestamp: {entry.timestamp}")
            if entry.metadata:
                print(f"   Metadata: {entry.metadata}")
            print("-" * 50)

    except Exception as e:
        print(f"Error viewing LTM: {e}")


def main():
    parser = argparse.ArgumentParser(description="View memory system data")
    parser.add_argument(
        "--backend", choices=["memory", "redis"], default="memory", help="STM backend"
    )
    parser.add_argument(
        "--redis-url", default="redis://localhost:6379", help="Redis URL"
    )
    parser.add_argument(
        "--view", choices=["stm", "ltm", "both"], default="both", help="What to view"
    )
    parser.add_argument("--session-id", help="Session ID for STM viewing")
    parser.add_argument("--user-id", help="User ID filter for LTM")
    parser.add_argument("--query", default="*", help="Search query for LTM")
    parser.add_argument("--limit", type=int, default=10, help="Max results for LTM")

    args = parser.parse_args()

    # Initialize memory manager
    memory_manager = MemoryManager(stm_backend=args.backend, redis_url=args.redis_url)

    if args.view in ["stm", "both"]:
        if not args.session_id:
            print("Error: --session-id required for STM viewing")
            return
        view_stm(memory_manager, args.session_id)

    if args.view in ["ltm", "both"]:
        view_ltm(memory_manager, args.user_id, args.query, args.limit)


if __name__ == "__main__":
    main()
