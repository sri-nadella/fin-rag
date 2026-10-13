# fin-rag: Retrieval-Augmented QA over SEC 10-K Filings

A question-answering system for company financial reports. It retrieves the most relevant passages from a 10-K filing and (soon) generates cited answers from them. The project focuses on **measuring** retrieval quality: three chunking strategies and four retrieval methods are compared on a golden question set.

> **Status:** work in progress. Ingestion, chunking, retrieval and evaluation are done. Generation, API/UI and CI are next.

## Pipeline

```
SEC EDGAR 10-K (HTML)
  -> parse.py   split into Items, keep table rows as single lines, drop footers
  -> chunk.py   3 strategies: fixed / recursive / section-aware
  -> dense.py   embeddings (bge-small-en-v1.5) stored in Qdrant
  -> hybrid.py  BM25 + dense, merged with Reciprocal Rank Fusion
  -> rerank.py  cross-encoder (bge-reranker-base) re-sorts the top 20
  -> run_eval.py  recall@k and MRR against a golden question set
```

## Chunking strategies

| Strategy | How it works |
|---|---|
| Fixed | 500-token windows, 50-token overlap, cuts anywhere |
| Recursive | Packs whole lines (sentences or table rows) up to 500 tokens |
| Section-aware | Recursive, plus a header on every chunk (`Apple Inc. 2025 10-K \| Item 7: ...`) |

## Results (preliminary)

Corpus: Apple Inc. FY2025 10-K. Golden set: 20 questions (18 are single-number lookups). A retrieved chunk counts as a hit if it contains the known answer string.

| Chunking | Method | R@1 | R@3 | R@5 | MRR |
|---|---|---|---|---|---|
| Fixed | dense | 0.60 | 0.95 | 0.95 | 0.76 |
| Fixed | bm25 | 0.80 | 0.85 | 0.95 | 0.85 |
| Fixed | hybrid | 0.75 | 1.00 | 1.00 | 0.87 |
| Fixed | hybrid + rerank | 0.70 | 0.95 | 1.00 | 0.80 |
| Recursive | dense | 0.40 | 0.85 | 0.95 | 0.62 |
| Recursive | bm25 | 0.65 | 0.95 | 0.95 | 0.79 |
| Recursive | hybrid | 0.60 | 1.00 | 1.00 | 0.77 |
| Recursive | hybrid + rerank | 0.65 | 0.95 | 0.95 | 0.78 |
| Section-aware | dense | 0.80 | 0.90 | 0.95 | 0.85 |
| Section-aware | bm25 | 0.65 | 0.85 | 0.95 | 0.76 |
| Section-aware | hybrid | 0.75 | 0.95 | 0.95 | 0.85 |
| **Section-aware** | **hybrid + rerank** | **0.90** | **1.00** | **1.00** | **0.94** |

**Headline:** baseline (fixed + dense) R@1 0.60 -> section-aware + hybrid + rerank R@1 0.90.

## Findings

- **Fixed chunking splits table rows.** A fixed cut separated the `Total net sales | 416,161` row across two chunks.
- **Dense search misses exact numbers in repeated tables.** "Weighted-average diluted shares" never reached the top 5 with dense retrieval, though two chunks contained the number. Hybrid retrieval fixed it for fixed and recursive chunks.
- **Reranking helped only section-aware chunks** (R@1 0.75 -> 0.90), and was flat or slightly negative on the others. Hypothesis: the header and whole rows give the cross-encoder coherent text to judge. Not yet tested.
- **BM25 did not help section-aware chunks.** The shared header adds common words that dilute keyword scoring.

## Limitations

- One company, one filing, 20 questions. One question equals 0.05, so gaps of 0.05-0.10 are noise.
- Most questions are number lookups, which favor keyword matching. Prose questions are being added.
- Answer strings were chosen from chunks the system had already produced, so the test is friendlier than a blind one.

## Quickstart

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ingest/download.py
python ingest/parse.py
python ingest/chunk.py
python retrieval/dense.py index
python eval/run_eval.py
```

## Roadmap

- [ ] Grow golden set to 40+ questions, including prose and blind-written ones
- [ ] LLM generation with inline citations and "I don't know" behavior
- [ ] Faithfulness and answer-relevance evaluation
- [ ] FastAPI backend and Streamlit UI
- [ ] Docker and GitHub Actions running the eval on every PR
- [ ] More companies and years
