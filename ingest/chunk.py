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

def chunk_recursive(text, size=500, overlap=50):
    """Pack whole lines into chunks of up to `size` tokens.
    Lines longer than `size` fall back to fixed-size splitting."""
    chunks, current, current_tokens = [], [], 0
    for line in text.split("\n"):
        t = count_tokens(line)
        if t > size:
            if current:
                chunks.append("\n".join(current))
                current, current_tokens = [], 0
            chunks.extend(chunk_fixed(line, size, overlap))
            continue
        if current_tokens + t > size and current:
            chunks.append("\n".join(current))
            current, current_tokens = [current[-1]], count_tokens(current[-1])
        current.append(line)
        current_tokens += t
    if current:
        chunks.append("\n".join(current))
    return chunks

def chunk_section_aware(text, header, size=500, overlap=50):
    """Recursive chunking, but every chunk starts with a context header."""
    budget = size - count_tokens(header) - 2
    pieces = chunk_recursive(text, size=budget, overlap=overlap)
    return [f"{header}\n{p}" for p in pieces]


def build_chunks(sections, company, ticker, year, strategy="fixed"):
    out = []
    for s in sections:
        if strategy == "section":
            header = f"{company} {year} 10-K | Item {s['item']}: {s['title']}"
            pieces = chunk_section_aware(s["text"], header)
        elif strategy == "recursive":
            pieces = chunk_recursive(s["text"])
        else:
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
    for strategy in ("fixed", "recursive", "section"):
        chunks = build_chunks(sections, "Apple Inc.", "AAPL", 2025, strategy)
        out = Path(f"data/processed/AAPL_chunks_{strategy}.jsonl")
        with out.open("w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c) + "\n")
        print(strategy, "-> total chunks:", len(chunks))