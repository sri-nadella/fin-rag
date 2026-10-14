import json
from pathlib import Path

questions = [json.loads(l) for l in Path("eval/golden.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
chunks = {
    s: [json.loads(l) for l in Path(f"data/processed/AAPL_chunks_{s}.jsonl").read_text(encoding="utf-8").splitlines()]
    for s in ("fixed", "recursive", "section")
}

bad = 0
for q in questions:
    counts = {s: sum(q["answer_contains"] in c["text"] for c in cs) for s, cs in chunks.items()}
    if min(counts.values()) == 0:
        bad += 1
        print("NOT FOUND in some strategy:", q["answer_contains"], counts, "|", q["question"])
print(f"{len(questions)} questions checked, {bad} problem(s)")