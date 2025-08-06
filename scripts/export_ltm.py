# scripts/export_ltm.py

import json
from app.memory.long_term import LongTermMemory
from app.config import settings
from datetime import datetime

EXPORT_FILE = f"ltm_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


def export_ltm(user_id: str = None):
    ltm = LongTermMemory()

    scroll_result = ltm.client.scroll(
        collection_name=ltm.collection_name,
        limit=1000,  # adjust as needed
        with_payload=True,
        with_vectors=True,
    )

    exported_data = []
    for point in scroll_result[0]:
        payload = point.payload
        if user_id and payload.get("user_id") != user_id:
            continue

        exported_data.append(
            {"id": str(point.id), "vector": point.vector, "payload": payload}
        )

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(exported_data, f, indent=4)

    print(f"✅ Exported {len(exported_data)} entries to {EXPORT_FILE}")


if __name__ == "__main__":
    export_ltm(user_id=None)
