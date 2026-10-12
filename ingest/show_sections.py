import re
from pathlib import Path
from bs4 import BeautifulSoup

# Find the downloaded filing
files = list(Path("data/raw").rglob("full-submission.txt"))
print("Found files:", files)

raw = files[0].read_text(encoding="utf-8", errors="ignore")

# The submission file wraps several documents; the 10-K is the first <DOCUMENT>
# whose TYPE is 10-K. Grab the text between <TEXT> and </TEXT> inside it.
m = re.search(r"<TYPE>10-K.*?<TEXT>(.*?)</TEXT>", raw, re.DOTALL | re.IGNORECASE)
body = m.group(1) if m else raw
print("Filing body length:", len(body))

soup = BeautifulSoup(body, "lxml")
text = soup.get_text("\n")
lines = [line.strip() for line in text.split("\n") if line.strip()]
print("Total lines:", len(lines))

# Print every line that looks like "Item 1A." or "Item 7."
for i, line in enumerate(lines):
    if re.match(r"^item\s+\d+[a-c]?\.?", line, re.IGNORECASE):
        print(i, "|", line[:80])