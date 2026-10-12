import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ITEM_RE = re.compile(r"^item\s+(\d+[a-c]?)\.\s*(.*)", re.IGNORECASE)


def load_lines(path):
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<TYPE>10-K.*?<TEXT>(.*?)</TEXT>", raw, re.DOTALL | re.IGNORECASE)
    body = m.group(1) if m else raw
    text = BeautifulSoup(body, "lxml").get_text("\n")
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def split_sections(lines):
    # find where each Item heading starts
    starts = []
    for i, ln in enumerate(lines):
        m = ITEM_RE.match(ln)
        if m:
            starts.append((i, m.group(1).upper(), m.group(2).strip()))
    sections = []
    for n, (i, item, title) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        body = "\n".join(lines[i + 1 : end])
        sections.append({"item": item, "title": title, "text": body})
    return sections


if __name__ == "__main__":
    path = next(Path("data/raw").rglob("full-submission.txt"))
    sections = split_sections(load_lines(path))
    out = Path("data/processed/AAPL_sections.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for s in sections:
            f.write(json.dumps(s) + "\n")
    for s in sections:
        print(f"Item {s['item']:<4} {len(s['text']):>8} chars  {s['title'][:50]}")