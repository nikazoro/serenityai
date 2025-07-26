import uuid
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "journal_entries"

class QdrantVectorStore:
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = int(port or os.getenv("QDRANT_PORT", 6333))
        self.client = QdrantClient(host=self.host, port=self.port)
        self._ensure_collection()

    def _ensure_collection(self):
        existing = [col.name for col in self.client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            self.client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

    def reset(self):
        """Deletes and recreates the collection"""
        self.client.delete_collection(collection_name=COLLECTION_NAME)
        self.client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"[Qdrant] Reset collection '{COLLECTION_NAME}'")

    def add_entry(self, vector: List[float], payload: Dict[str, Any], point_id: Optional[str] = None):
        point_id = point_id or str(uuid.uuid4())
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)]
        )

    def batch_add_entries(self, entries: List[Dict[str, Any]]):
        """entries: list of {'vector': [...], 'payload': {...}, 'id': Optional[str]}"""
        points = [
            PointStruct(
                id=entry.get("id", str(uuid.uuid4())),
                vector=entry["vector"],
                payload=entry["payload"]
            )
            for entry in entries
        ]
        self.client.upsert(collection_name=COLLECTION_NAME, points=points)

    def search(self, query_vector: List[float], top_k: int = 3, filters: Optional[Dict[str, str]] = None):
        qdrant_filter = None
        if filters:
            qdrant_filter = Filter(
                must=[
                    FieldCondition(key=key, match=MatchValue(value=value))
                    for key, value in filters.items()
                ]
            )
        return self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter
        )
