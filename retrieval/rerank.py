import sys

sys.path.insert(0, ".")
from sentence_transformers import CrossEncoder
from retrieval.hybrid import hybrid_search

reranker = CrossEncoder("BAAI/bge-reranker-base")


def rerank_search(query, strategy, k=5, pool=20):
    """Get a wide pool with hybrid search, then re-sort it with a cross-encoder."""
    candidates = hybrid_search(query, strategy, k=pool, pool=pool)
    scores = reranker.predict([(query, c["text"]) for c in candidates])
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    return [c for _, c in ranked[:k]]