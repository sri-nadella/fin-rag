import sys

sys.path.insert(0, ".")
import ollama
from retrieval.rerank import rerank_search

MODEL = "qwen2.5:7b"
STRATEGY = "section"

PROMPT = """You answer questions about a company's 10-K filing using ONLY the context below.
Rules:
- After EVERY factual statement, add a citation like [1] or [2] matching the context numbers.
- Financial tables are in millions of dollars unless stated otherwise. Say "$X million".
- In table rows like "Label | A | pct | B | pct | C", the large numbers are dollar amounts and small numbers after them are percent changes. Answer with the TOTAL row for the exact year asked, not a segment row. Write units exactly: "$X million".
- If the context does not contain the answer, reply exactly: I don't know based on the provided documents.
- Do not use outside knowledge. Keep the answer short.

Context:
{context}

Question: {question}
Answer:"""


def answer(question, k=4):
    chunks = rerank_search(question, STRATEGY, k=k)
    context = "\n\n".join(
        f"[{i}] ({c['section_title']}) {c['text']}" for i, c in enumerate(chunks, start=1)
    )
    resp = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
        options={"temperature": 0},
    )
    return resp["message"]["content"], chunks


if __name__ == "__main__":
    q = sys.argv[1]
    text, chunks = answer(q)
    print("\nANSWER:\n" + text)
    print("\nSOURCES:")
    for i, c in enumerate(chunks, start=1):
        print(f"[{i}] {c['chunk_id']}")