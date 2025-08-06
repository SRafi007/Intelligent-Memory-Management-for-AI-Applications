# scripts/import_ltm.py

import json
from app.memory.long_term import LongTermMemory
from app.config import settings
from qdrant_client.http.models import PointStruct

IMPORT_FILE = "ltm_export_file.json"  # Replace with your export filename


def import_ltm():
    ltm = LongTermMemory()

    with open(IMPORT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    points = [
        PointStruct(id=item["id"], vector=item["vector"], payload=item["payload"])
        for item in data
    ]

    ltm.client.upsert(collection_name=ltm.collection_name, points=points)
    print(f"✅ Imported {len(points)} entries into collection: {ltm.collection_name}")


if __name__ == "__main__":
    import_ltm()
