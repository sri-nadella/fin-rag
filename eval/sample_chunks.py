import json
import random
from pathlib import Path

chunks = [json.loads(l) for l in Path("data/processed/AAPL_chunks_section.jsonl").read_text(encoding="utf-8").splitlines()]
risk = [c for c in chunks if c["item"] == "1A"]
for c in random.sample(risk, 5):
    print("=====", c["chunk_id"])
    print(c["text"][:900])
    print()