import json
from pathlib import Path

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text):
    return len(enc.encode(text))


def chunk_fixed(text, size=500, overlap=50):
    """Fixed-size chunking: slide a window of `size` tokens over the text."""
    tokens = enc.encode(text)
    step = size - overlap
    chunks = []
    for start in range(0, len(tokens), step):
        piece = tokens[start : start + size]
        if piece:
            chunks.append(enc.decode(piece))
        if start + size >= len(tokens):
            break
    return chunks


def build_chunks(sections, company, ticker, year, strategy="fixed"):
    out = []
    for s in sections:
        pieces = chunk_fixed(s["text"])
        for n, piece in enumerate(pieces):
            out.append(
                {
                    "chunk_id": f"{ticker}-{year}-item{s['item']}-{n}",
                    "company": company,
                    "ticker": ticker,
                    "fiscal_year": year,
                    "item": s["item"],
                    "section_title": s["title"],
                    "chunk_strategy": strategy,
                    "token_count": count_tokens(piece),
                    "text": piece,
                }
            )
    return out


if __name__ == "__main__":
    sections = [
        json.loads(line)
        for line in Path("data/processed/AAPL_sections.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    chunks = build_chunks(sections, "Apple Inc.", "AAPL", 2025)
    out = Path("data/processed/AAPL_chunks_fixed.jsonl")
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    print("Total chunks:", len(chunks))
    for c in chunks[:3]:
        print("---", c["chunk_id"], c["token_count"], "tokens")
        print(c["text"][:300])