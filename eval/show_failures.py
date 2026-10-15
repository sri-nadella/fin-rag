import json
from pathlib import Path

rows = [json.loads(l) for l in Path("eval/runs/gen_results.jsonl").read_text(encoding="utf-8").splitlines()]
for r in rows:
    if r["type"] == "answerable" and not r["correct"]:
        print("Q:", r["question"])
        print("EXPECTED:", r["expected"])
        print("ANSWER:", r["answer"][:300].replace("\n", " "))
        print()