import sys

sys.path.insert(0, ".")
from ingest.chunk import chunk_fixed, chunk_recursive, count_tokens


def test_fixed_chunks_respect_size():
    text = "word " * 2000
    chunks = chunk_fixed(text, size=500, overlap=50)
    assert len(chunks) > 1
    assert all(count_tokens(c) <= 500 for c in chunks)


def test_recursive_keeps_whole_lines():
    lines = [f"Row {i} | {i * 1000:,} | {i}" for i in range(300)]
    chunks = chunk_recursive("\n".join(lines), size=200)
    for c in chunks:
        for line in c.split("\n"):
            assert line in lines


def test_recursive_empty_text():
    assert chunk_recursive("", size=200) in ([], [""])