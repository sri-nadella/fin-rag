import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from retrieval.dense import search as dense_search
from retrieval.hybrid import bm25_search, hybrid_search
from retrieval.rerank import rerank_search

questions = [
    json.loads(l)
    for l in Path("eval/golden.jsonl").read_text(encoding="utf-8").splitlines()
    if l.strip()
]

methods = {
    "dense": lambda q, s: [h.payload for h in dense_search(q, s, k=5)],
    "bm25": lambda q, s: bm25_search(q, s, k=5),
    "hybrid": lambda q, s: hybrid_search(q, s, k=5),
    "rerank": lambda q, s: rerank_search(q, s, k=5),
}

print(f"{len(questions)} questions")
print(f"{'strategy':<10} {'method':<8} {'R@1':>5} {'R@3':>5} {'R@5':>5} {'MRR':>5}")
for strategy in ("fixed", "recursive", "section"):
    for name, fn in methods.items():
        ranks = []
        for q in questions:
            rank = None
            for i, c in enumerate(fn(q["question"], strategy), start=1):
                if q["answer_contains"] in c["text"]:
                    rank = i
                    break
            ranks.append(rank)
        n = len(ranks)
        r = lambda k: sum(1 for x in ranks if x and x <= k) / n
        mrr = sum(1 / x for x in ranks if x) / n
        print(f"{strategy:<10} {name:<8} {r(1):>5.2f} {r(3):>5.2f} {r(5):>5.2f} {mrr:>5.2f}")