import app.config as config

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


QDRANT_IP = f"{config.QDRANT_IP_ADDRESS}"
COLLECTION_NAME = config.QDRANT_COLLECTION_NAME

client = QdrantClient(QDRANT_IP)

def create_collection_if_not_exists():
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

def point_exists(point_id: int) -> bool:
    result = client.retrieve(collection_name=COLLECTION_NAME, ids=[point_id])
    return len(result) > 0

def add_point_to_qdrant(point_id: int, vector: list[float], payload: dict):
    if point_exists(point_id):
        return
    point = PointStruct(id=point_id, vector=vector, payload=payload)
    client.upsert(collection_name=COLLECTION_NAME, points=[point])