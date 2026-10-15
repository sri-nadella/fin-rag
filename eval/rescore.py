import json
import re
from pathlib import Path


def norm(s):
    return re.sub(r"[^a-z0-9.]", "", s.lower())


rows = [json.loads(l) for l in Path("eval/runs/gen_results.jsonl").read_text(encoding="utf-8").splitlines()]
a = [r for r in rows if r["type"] == "answerable"]
ok = sum(norm(r["expected"]) in norm(r["answer"]) for r in a)
print(f"Normalised match: {ok}/{len(a)} = {ok/len(a):.2f}")