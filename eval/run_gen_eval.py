import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
from generation.answer import answer

limit = int(sys.argv[1]) if len(sys.argv) > 1 else None


def load(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


golden = load("eval/golden.jsonl")
unans = load("eval/unanswerable.jsonl")
if limit:
    golden, unans = golden[:limit], unans[: max(2, limit // 3)]

rows = []
start = time.time()

for q in golden:
    text, chunks = answer(q["question"])
    cites = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    rows.append(
        {
            "type": "answerable",
            "question": q["question"],
            "expected": q["answer_contains"],
            "answer": text,
            "correct": q["answer_contains"].lower() in text.lower(),
            "cited": bool(cites),
            "valid_cites": bool(cites) and all(1 <= n <= len(chunks) for n in cites),
            "refused": "i don't know" in text.lower(),
        }
    )
    print(f"[{len(rows)}] correct={rows[-1]['correct']} cited={rows[-1]['cited']} | {q['question'][:60]}", flush=True)

for q in unans:
    text, chunks = answer(q["question"])
    rows.append(
        {
            "type": "unanswerable",
            "question": q["question"],
            "answer": text,
            "refused": "i don't know" in text.lower(),
        }
    )
    print(f"[{len(rows)}] refused={rows[-1]['refused']} | {q['question'][:60]}", flush=True)

Path("eval/runs").mkdir(exist_ok=True)
Path("eval/runs/gen_results.jsonl").write_text(
    "\n".join(json.dumps(r) for r in rows), encoding="utf-8"
)

a = [r for r in rows if r["type"] == "answerable"]
u = [r for r in rows if r["type"] == "unanswerable"]
n = len(a)
print("\n===== GENERATION RESULTS =====")
print(f"Answerable questions: {n}")
print(f"  Answer contains expected value: {sum(r['correct'] for r in a) / n:.2f}")
print(f"  Has citation [n]:               {sum(r['cited'] for r in a) / n:.2f}")
print(f"  Citations point to real chunks: {sum(r['valid_cites'] for r in a) / n:.2f}")
print(f"  Wrongly refused:                {sum(r['refused'] for r in a) / n:.2f}")
print(f"Unanswerable questions: {len(u)}")
print(f"  Correctly refused:              {sum(r['refused'] for r in u) / len(u):.2f}")
print(f"Time: {(time.time() - start) / 60:.1f} min")