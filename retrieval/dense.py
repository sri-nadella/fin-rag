import json
import sys
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

model = SentenceTransformer(MODEL_NAME)
client = QdrantClient(path="qdrant_data")  # stored in a local folder, no Docker needed


def build_index(strategy):
    path = Path(f"data/processed/AAPL_chunks_{strategy}.jsonl")
    chunks = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    texts = [c["text"] for c in chunks]
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    name = f"aapl_{strategy}"
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=vectors.shape[1], distance=Distance.COSINE),
    )
    client.upsert(
        collection_name=name,
        points=[
            PointStruct(id=i, vector=v.tolist(), payload=c)
            for i, (v, c) in enumerate(zip(vectors, chunks))
        ],
    )
    print(f"Indexed {len(chunks)} chunks into {name}")


def search(query, strategy="recursive", k=5):
    qvec = model.encode(QUERY_PREFIX + query, normalize_embeddings=True).tolist()
    return client.query_points(collection_name=f"aapl_{strategy}", query=qvec, limit=k).points


if __name__ == "__main__":
    if sys.argv[1] == "index":
        for s in ("fixed", "recursive", "section"):
            build_index(s)
    else:
        query = sys.argv[1]
        strategy = sys.argv[2] if len(sys.argv) > 2 else "recursive"
        for h in search(query, strategy):
            p = h.payload
            print(f"\n[{h.score:.3f}] {p['chunk_id']} (Item {p['item']}: {p['section_title'][:40]})")
            print(p["text"][:300].replace("\n", " / "))
    client.close()