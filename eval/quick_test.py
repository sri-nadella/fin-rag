import sys

sys.path.insert(0, ".")
from generation.answer import answer

tests = [
    ("What was Apple's operating income in 2025?", "133,050"),
    ("What was Apple's operating income in 2024?", "123,216"),
    ("What were Apple's total net sales in fiscal 2024?", "391,035"),
    ("What were Japan net sales in 2024?", "25,052"),
    ("How much deferred revenue does Apple expect to realize in less than a year?", "66"),
    ("What was Apple's total net sales in 2025?", "416,161"),
]
ok = 0
for q, expected in tests:
    text, _ = answer(q)
    hit = expected in text
    ok += hit
    print(("PASS" if hit else "FAIL"), "|", q, "->", text[:120].replace("\n", " "), flush=True)
print(f"{ok}/{len(tests)} passed")