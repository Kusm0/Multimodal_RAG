import app.config as config

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue



QDRANT_IP = config.QDRANT_IP_ADDRESS
COLLECTION_NAME = config.QDRANT_COLLECTION_NAME

client = QdrantClient(QDRANT_IP)

def retrieve_similar_chunks(query_vector, top_k: int = 3, filter_by_type: str = None):
   # query_vector = get_query_embedding(query)

    filters = None
    if filter_by_type:
        filters = Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=filter_by_type))]
        )

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=filters
    )

    return results

