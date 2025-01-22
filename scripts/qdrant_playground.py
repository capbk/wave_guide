from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct, Filter, FieldCondition, MatchValue

from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

client = QdrantClient(
    os.getenv("QDRANT_CLUSTER_NAME"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

collections = client.get_collections()
collection_names = [collection.name for collection in collections.collections]
# create collection and populate

if "test_collection" not in collection_names:
    print("Creating collection")

    client.create_collection(
        collection_name="test_collection",
        vectors_config=VectorParams(size=4, distance=Distance.DOT),
    )


    operation_info = client.upsert(
        collection_name="test_collection",
        wait=True,
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
            PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
            PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
            PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
            PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
            PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
        ],
    )

    print(operation_info)

# search

hits = client.search(
    collection_name="test_collection",
    query_vector=[0.2, 0.1, 0.9, 0.7],
    limit=3
)
print("search without filter")
print(hits)

# search with filter

search_result = client.search(
    collection_name="test_collection",
    query_vector=[0.2, 0.1, 0.9, 0.7],
    query_filter=Filter(
        must=[FieldCondition(key="city", match=MatchValue(value="London"))]
    ),
    with_payload=True,
    limit=3,
)
print("search with filter")
print(search_result)