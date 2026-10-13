import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from retrieval.dense import search

K = 5
questions = [
    json.loads(l)
    for l in Path("eval/golden.jsonl").read_text(encoding="utf-8").splitlines()
    if l.strip()
]

for strategy in ("fixed", "recursive", "section"):
    hits, reciprocal_ranks = 0, 0.0
    for q in questions:
        results = search(q["question"], strategy, k=K)
        rank = None
        for i, h in enumerate(results, start=1):
            if q["answer_contains"] in h.payload["text"]:
                rank = i
                break
        if rank:
            hits += 1
            reciprocal_ranks += 1 / rank
    n = len(questions)
    print(f"{strategy:<10} recall@{K} = {hits / n:.2f}   MRR = {reciprocal_ranks / n:.2f}")