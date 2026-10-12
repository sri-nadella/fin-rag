import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ITEM_RE = re.compile(r"^item\s+(\d+[a-c]?)\.\s*(.*)", re.IGNORECASE)
FOOTER_RE = re.compile(r"^Apple Inc\.\s*\|?\s*\d{4} Form 10-K\s*\|?\s*\d+$")


def load_lines(path):
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<TYPE>10-K.*?<TEXT>(.*?)</TEXT>", raw, re.DOTALL | re.IGNORECASE)
    body = m.group(1) if m else raw
    soup = BeautifulSoup(body, "lxml")

    # 1. Turn each table row into one line: "Net sales | 416,161 | 391,035"
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c and c not in ("$", "%", ")")]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))

    # 2. Join inline text with spaces; split lines only on block elements
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for tag in soup.find_all(["p", "div", "li", "h1", "h2", "h3", "h4"]):
        tag.append("\n")
    text = soup.get_text(" ")

    # 3. Tidy whitespace and drop page footers
    lines = []
    for ln in text.split("\n"):
        ln = re.sub(r"\s*[®™]\s*", " ", ln)
        ln = re.sub(r"\s+", " ", ln).strip()
        if not ln or FOOTER_RE.match(ln):
            continue
        lines.append(ln)
    return lines


def split_sections(lines):
    starts = []
    for i, ln in enumerate(lines):
        m = ITEM_RE.match(ln)
        if m:
            title = m.group(2).strip()
            # table-of-contents rows look like "Item 1. | Business | 1": skip them
            if not title or "|" in title:
                continue
            starts.append((i, m.group(1).upper(), title))
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