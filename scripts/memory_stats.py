# scripts/memory_stats.py
#!/usr/bin/env python3
"""
Script to show memory system statistics
"""

import argparse
import sys
import os
from collections import Counter

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.memory.memory_manager import MemoryManager
from qdrant_client import QdrantClient
from app.config.settings import *


def show_stm_stats(memory_manager: MemoryManager, session_id: str):
    """Show STM statistics"""
    print(f"\n=== STM Statistics (Session: {session_id}) ===")
    stm_data = memory_manager.get_all_short_term(session_id)

    print(f"Total entries: {len(stm_data)}")
    if stm_data:
        avg_length = sum(len(v) for v in stm_data.values()) / len(stm_data)
        print(f"Average text length: {avg_length:.1f} characters")


def show_ltm_stats(collection_name: str):
    """Show LTM statistics"""
    print(f"\n=== LTM Statistics (Collection: {collection_name}) ===")

    try:
        client = QdrantClient(host=LTM_QDRANT_HOST, port=LTM_QDRANT_PORT)

        if not client.collection_exists(collection_name):
            print(f"Collection '{collection_name}' does not exist.")
            return

        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"Total points: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        print(f"Distance metric: {collection_info.config.params.vectors.distance}")

        # Get some sample points to analyze
        sample_points = client.scroll(
            collection_name=collection_name, limit=100, with_payload=True
        )[
            0
        ]  # Get first element (points list)

        if sample_points:
            # Analyze users
            users = [
                point.payload.get("user_id")
                for point in sample_points
                if point.payload.get("user_id")
            ]
            user_counts = Counter(users)
            print(f"\nUser distribution (top 5):")
            for user, count in user_counts.most_common(5):
                print(f"  {user}: {count} entries")

            # Analyze importance scores
            importance_scores = [
                point.payload.get("metadata", {}).get("importance", 0)
                for point in sample_points
            ]
            if importance_scores:
                avg_importance = sum(importance_scores) / len(importance_scores)
                print(f"\nAverage importance score: {avg_importance:.3f}")
                print(f"Max importance score: {max(importance_scores):.3f}")
                print(f"Min importance score: {min(importance_scores):.3f}")

            # Analyze text lengths
            text_lengths = [
                len(point.payload.get("text", "")) for point in sample_points
            ]
            if text_lengths:
                avg_length = sum(text_lengths) / len(text_lengths)
                print(f"\nAverage text length: {avg_length:.1f} characters")
                print(f"Max text length: {max(text_lengths)} characters")
                print(f"Min text length: {min(text_lengths)} characters")

    except Exception as e:
        print(f"Error getting LTM stats: {e}")


def main():
    parser = argparse.ArgumentParser(description="Show memory system statistics")
    parser.add_argument(
        "--backend", choices=["memory", "redis"], default="memory", help="STM backend"
    )
    parser.add_argument(
        "--redis-url", default="redis://localhost:6379", help="Redis URL"
    )
    parser.add_argument(
        "--show",
        choices=["stm", "ltm", "both"],
        default="both",
        help="What stats to show",
    )
    parser.add_argument("--session-id", help="Session ID for STM stats")
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

    if args.show in ["stm", "both"]:
        if not args.session_id:
            print("Warning: --session-id required for STM stats")
        else:
            show_stm_stats(memory_manager, args.session_id)

    if args.show in ["ltm", "both"]:
        show_ltm_stats(args.collection)


if __name__ == "__main__":
    main()
