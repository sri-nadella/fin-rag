import sys
import time

sys.path.insert(0, ".")
from fastapi import FastAPI
from pydantic import BaseModel

from generation.answer import answer

app = FastAPI(title="fin-rag")

MODELS = {"fast": "llama3.2:3b", "accurate": "qwen2.5:7b"}


class AskRequest(BaseModel):
    question: str
    mode: str = "fast"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    start = time.time()
    text, chunks = answer(req.question, model=MODELS.get(req.mode, MODELS["fast"]))
    return {
        "answer": text,
        "mode": req.mode,
        "seconds": round(time.time() - start, 1),
        "sources": [
            {"n": i, "chunk_id": c["chunk_id"], "section": c["section_title"], "text": c["text"]}
            for i, c in enumerate(chunks, start=1)
        ],
    }