# examples/view_ltm.py

from app.memory.long_term import LongTermMemory
from app.config import settings
from pprint import pprint


def view_all_entries(user_id: str = None):
    ltm = LongTermMemory()

    print(
        f"\n📦 Fetching all LTM entries from collection: {settings.LTM_COLLECTION_NAME}"
    )

    # Access all stored points directly
    scroll_result = ltm.client.scroll(
        collection_name=ltm.collection_name,
        limit=100,  # You can increase this or paginate
        with_payload=True,
        with_vectors=False,
    )

    if not scroll_result or not scroll_result[0]:
        print("⚠️ No entries found.")
        return

    for point in scroll_result[0]:
        payload = point.payload
        if user_id and payload.get("user_id") != user_id:
            continue

        print("\n🧠 Entry:")
        print(f"🔹 ID: {point.id}")
        print(f"👤 User: {payload.get('user_id')}")
        print(f"📝 Text: {payload.get('text')}")
        print(f"🗂️ Metadata: {payload.get('metadata')}")
        print("—" * 30)


if __name__ == "__main__":
    # Optional: Replace with a specific user ID if needed
    view_all_entries(user_id=None)
