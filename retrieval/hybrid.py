import json
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")
from rank_bm25 import BM25Okapi
from retrieval.dense import search as dense_search


def tokenize(text):
    return re.findall(r"[a-z0-9][a-z0-9,\.]*", text.lower())


_cache = {}


def _bm25(strategy):
    if strategy not in _cache:
        path = Path(f"data/processed/AAPL_chunks_{strategy}.jsonl")
        chunks = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
        _cache[strategy] = (BM25Okapi([tokenize(c["text"]) for c in chunks]), chunks)
    return _cache[strategy]


def bm25_search(query, strategy, k=5):
    bm25, chunks = _bm25(strategy)
    scores = bm25.get_scores(tokenize(query))
    top = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:k]
    return [chunks[i] for i in top]


def hybrid_search(query, strategy, k=5, pool=20):
    """Reciprocal Rank Fusion of dense and BM25 rankings."""
    dense = [h.payload for h in dense_search(query, strategy, k=pool)]
    sparse = bm25_search(query, strategy, k=pool)
    scores, by_id = {}, {}
    for ranking in (dense, sparse):
        for rank, c in enumerate(ranking, start=1):
            scores[c["chunk_id"]] = scores.get(c["chunk_id"], 0) + 1 / (60 + rank)
            by_id[c["chunk_id"]] = c
    best = sorted(scores, key=scores.get, reverse=True)[:k]
    return [by_id[i] for i in best]