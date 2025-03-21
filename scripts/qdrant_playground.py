from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct, Filter, FieldCondition, MatchValue

from dotenv import load_dotenv
import os

from get_acoustic_brainz_data import ingest_json

# Load environment variables from .env file
load_dotenv()

client = QdrantClient(
    os.getenv("QDRANT_CLUSTER_NAME"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

collections = client.get_collections()
collection_names = [collection.name for collection in collections.collections]
# create collection and populate

if "tracks" not in collection_names:
    print("Creating collection")

    client.create_collection(
        collection_name="tracks",
        vectors_config=VectorParams(size=11, distance=Distance.COSINE),
    )

# TODO: loop through directory until we get to 190,000 points
tracks_dicts = ingest_json("/Users/jeffreycapobianco/coding/wave_guide/data/acousticbrainz-highlevel-json-20220623/highlevel/00/0/")
points = []
for track in tracks_dicts:
    points.append(PointStruct(
        id=track['musicbrainz_recordingid'], 
        vector=[
            track['acoustic'],
            track['aggressive'],
            track['danceable'],
            track['dark'],
            track['electronic'],
            track['happy'],
            track['party'],
            track['relaxed'],
            track['sad'],
            track['tonal'],
            track['voice']
        ], 
        payload={
            'title': track['title'],
            'artist': track['artist'],
            'album': track['album'],
            'musicbrainz_recordingid': track['musicbrainz_recordingid']
        }
    ))

operation_info = client.upsert(
    collection_name="tracks",
    wait=True,
    points=points
)

print(operation_info)

# search

hits = client.search(
    collection_name="tracks",
    query_vector=[0.2, 0.1, 0.9, 0.7, 0.2, 0.1, 0.9, 0.7, 0.2, 0.1, 0.9],
    limit=3
)
print("search without filter")
print(hits)

# search with filter

# search_result = client.search(
#     collection_name="tracks",
#     query_vector=[0.2, 0.1, 0.9, 0.7, 0.2, 0.1, 0.9, 0.7, 0.2, 0.1, 0.9],
#     query_filter=Filter(
#         must=[FieldCondition(key="city", match=MatchValue(value="London"))]
#     ),
#     with_payload=True,
#     limit=3,
# )
# print("search with filter")
# print(search_result)