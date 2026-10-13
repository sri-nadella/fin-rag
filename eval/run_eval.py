import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from retrieval.dense import search

questions = [
    json.loads(l)
    for l in Path("eval/golden.jsonl").read_text(encoding="utf-8").splitlines()
    if l.strip()
]

print(f"{len(questions)} questions")
print(f"{'strategy':<10} {'R@1':>5} {'R@3':>5} {'R@5':>5} {'MRR':>5}")
for strategy in ("fixed", "recursive", "section"):
    ranks = []
    for q in questions:
        results = search(q["question"], strategy, k=5)
        rank = None
        for i, h in enumerate(results, start=1):
            if q["answer_contains"] in h.payload["text"]:
                rank = i
                break
        ranks.append(rank)
    n = len(ranks)
    r = lambda k: sum(1 for x in ranks if x and x <= k) / n
    mrr = sum(1 / x for x in ranks if x) / n
    print(f"{strategy:<10} {r(1):>5.2f} {r(3):>5.2f} {r(5):>5.2f} {mrr:>5.2f}")
    misses = [questions[i]["question"] for i, x in enumerate(ranks) if x is None]
    for m in misses:
        print("   MISS:", m)