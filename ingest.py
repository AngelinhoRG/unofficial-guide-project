"""
ingest.py — Milestone 3: Document ingestion and chunking

Sources:
  - Reddit threads: loaded from manually saved .txt files in documents/
  - OMS Central reviews: scraped via requests + BeautifulSoup
  - Sac State course catalog: scraped via requests + BeautifulSoup

Chunk size:  ~300 tokens ≈ 1200 characters (mid-point of the 250–350 token range)
Overlap:      ~25 tokens ≈  100 characters

Saves results to documents/chunks.json for use in Milestone 4 (embedding).
"""

import html as html_module
import json
import re
import time
import os
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHUNK_SIZE = 1200      # ~300 tokens at ~4 chars/token
CHUNK_OVERLAP = 100    # ~25 tokens
OUTPUT_PATH = os.path.join("documents", "chunks.json")
RAW_DIR = os.path.join("documents", "raw")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; unofficial-guide-bot/1.0)"
}

# ---------------------------------------------------------------------------
# Fetching helpers
# ---------------------------------------------------------------------------

def load_local_file(filepath: str, source_id: int, source_url: str) -> list[dict]:
    """
    Load a manually saved Reddit thread text file.
    Splits on blank lines so each paragraph / comment block becomes its own doc.
    Skips blocks that look like thread titles (questions, not answers).
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"  [WARN] File not found: {filepath}")
        return []

    blocks = re.split(r"\n\s*\n", raw)
    docs = []
    for block in blocks:
        text = block.strip()
        # Skip short fragments and thread-title questions (no substantive opinion)
        if len(text) < 80:
            continue
        if text.endswith("?") and len(text) < 200:
            continue
        docs.append({
            "text": text,
            "source_id": source_id,
            "source_url": source_url,
            "source_type": "reddit_comment",
        })
    return docs


def fetch_omscentral_reviews(url: str, source_id: int) -> list[dict]:
    """
    Scrape review text from an OMS Central course review page.
    Each review card's text block becomes one raw document.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [WARN] Could not fetch {url}: {exc}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    docs = []

    # div.wrap-break-word contains one full review per div (multi-paragraph)
    review_divs = soup.select("div.wrap-break-word")
    if not review_divs:
        # Fallback if OMS Central changes their markup
        review_divs = soup.select("div.review-body") or soup.find_all("article")

    for div in review_divs:
        text = div.get_text(separator="\n", strip=True)
        if len(text) < 50:
            continue
        docs.append({
            "text": text,
            "source_id": source_id,
            "source_url": url,
            "source_type": "omscentral_review",
        })
    return docs


def fetch_sacstate_catalog(url: str, source_id: int) -> list[dict]:
    """
    Scrape course descriptions from the Sac State CSC catalog page.
    Each course block becomes one raw document.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [WARN] Could not fetch {url}: {exc}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    docs = []

    course_blocks = soup.select("div.courseblock") or soup.select(".course-description")
    if not course_blocks:
        course_blocks = [p for p in soup.find_all("p") if len(p.get_text(strip=True)) > 60]

    for block in course_blocks:
        text = re.sub(r"\s+", " ", block.get_text(separator=" ", strip=True))
        if len(text) < 40:
            continue
        docs.append({
            "text": text,
            "source_id": source_id,
            "source_url": url,
            "source_type": "course_catalog",
        })
    return docs


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Remove all non-substantive content and normalize text:
    - HTML entities (&amp; &#x27; etc.)
    - Bare URLs
    - Markdown formatting (bold, italic, links, blockquotes, headings)
    - UI boilerplate phrases (share, reply, report, read more, etc.)
    - Excess whitespace
    """
    # Decode HTML entities first (&amp; → &, &#x27; → ', &nbsp; → space, etc.)
    text = html_module.unescape(text)

    # Remove bare URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove markdown formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)              # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)                   # italic
    text = re.sub(r"~~(.+?)~~", r"\1", text)                   # strikethrough
    text = re.sub(r"`(.+?)`", r"\1", text)                     # inline code
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)      # links → anchor text
    text = re.sub(r"^>+\s?", "", text, flags=re.MULTILINE)     # blockquotes
    text = re.sub(r"^#+\s.*$", "", text, flags=re.MULTILINE)   # heading lines

    # Remove UI boilerplate lines (share buttons, nav, counters)
    boilerplate = re.compile(
        r"^(share|reply|report|save|hide|load more|read more|"
        r"sign in|log in|log out|subscribe|back to top|"
        r"view all comments|\d+ (comments?|points?|votes?|upvotes?)|"
        r"posted by|submitted by|permalink|embed|parent)[\s:]*$",
        re.IGNORECASE | re.MULTILINE,
    )
    text = boilerplate.sub("", text)

    # Collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Source definitions
# ---------------------------------------------------------------------------

DOCS_DIR = "documents"

SOURCES = [
    # Reddit sources — loaded from local .txt files
    (1,  lambda url, sid: load_local_file(os.path.join(DOCS_DIR, "free_time.txt"), sid, url),
         "https://www.reddit.com/r/csMajors/comments/tyd551/as_a_cs_undergraduate_how_much_free_time_do_you/"),

    (2,  lambda url, sid: load_local_file(os.path.join(DOCS_DIR, "study_hours_per_week.txt"), sid, url),
         "https://www.reddit.com/r/berkeley/comments/19as3vo/choosing_between_cs_courses_workload_and_advice/"),

    (3,  lambda url, sid: load_local_file(os.path.join(DOCS_DIR, "intro_class_workloads.txt"), sid, url),
         "https://www.reddit.com/r/BrownU/comments/mwzx77/how_is_the_workload_for_intro_cs_classes_how_many/"),

    (4,  lambda url, sid: load_local_file(os.path.join(DOCS_DIR, "reddit_hours_per_week.txt"), sid, url),
         "https://www.reddit.com/r/csMajors/comments/9q87g2/cs_majors_how_many_hours_per_week_do_you/"),

    (10, lambda url, sid: load_local_file(os.path.join(DOCS_DIR, "how_to_manage_heavy_workload_classes.txt"), sid, url),
         "https://www.reddit.com/r/csMajors/comments/13ie714/how_to_manage_time_with_heavy_workload_classes/"),

    # Web sources
    (5,  fetch_sacstate_catalog,    "https://catalog.csus.edu/courses-a-z/csc/"),
    (6,  fetch_omscentral_reviews,  "https://www.omscentral.com/courses/machine-learning/reviews"),
    (7,  fetch_omscentral_reviews,  "https://www.omscentral.com/courses/computer-networks/reviews"),
    (8,  fetch_omscentral_reviews,  "https://www.omscentral.com/courses/software-development-process/reviews"),
    (9,  fetch_omscentral_reviews,  "http://omscentral.com/courses/artificial-intelligence/reviews"),
]


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def save_raw(source_id: int, docs: list[dict]) -> None:
    """Write unprocessed text for one source to documents/raw/source_<id>.json."""
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, f"source_{source_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)


def ingest_all() -> list[dict]:
    """
    Fetch all sources, save raw text to documents/raw/ before any cleaning,
    then clean and return a flat list of doc dicts.
    """
    all_docs = []
    for source_id, fetch_fn, url in SOURCES:
        print(f"Fetching source {source_id}: {url}")
        raw_docs = fetch_fn(url, source_id)
        save_raw(source_id, raw_docs)           # persist raw text first
        for doc in raw_docs:
            doc["text"] = clean_text(doc["text"])
        raw_docs = [d for d in raw_docs if len(d["text"]) >= 30]
        print(f"  -> {len(raw_docs)} documents retrieved")
        all_docs.extend(raw_docs)
        time.sleep(1)
    return all_docs


def merge_short_docs(docs: list[dict]) -> list[dict]:
    """
    Merge consecutive short documents from the same source into larger units
    so chunks reach the 250-token floor (~1000 chars) after splitting.

    Documents are joined with a blank line so the splitter can still break
    at paragraph boundaries if the merged block exceeds CHUNK_SIZE.
    """
    merged = []
    buffer_text = ""
    buffer_meta = None

    for doc in docs:
        same_source = buffer_meta and buffer_meta["source_id"] == doc["source_id"]

        if same_source and len(buffer_text) + len(doc["text"]) + 2 <= CHUNK_SIZE * 3:
            buffer_text += "\n\n" + doc["text"]
        else:
            if buffer_text and buffer_meta:
                merged.append({**buffer_meta, "text": buffer_text})
            buffer_text = doc["text"]
            buffer_meta = {k: v for k, v in doc.items() if k != "text"}

    if buffer_text and buffer_meta:
        merged.append({**buffer_meta, "text": buffer_text})

    return merged


def chunk_documents(docs: list[dict]) -> list[dict]:
    """
    Merge short docs first, then split with RecursiveCharacterTextSplitter.
    Separators prioritize paragraph and sentence boundaries to keep
    review-sized semantic units intact.
    """
    docs = merge_short_docs(docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )

    chunks = []
    for doc_idx, doc in enumerate(docs):
        splits = splitter.split_text(doc["text"])
        for chunk_idx, chunk_text in enumerate(splits):
            if len(chunk_text.strip()) < 40:
                continue
            chunks.append({
                "chunk_id": f"doc{doc_idx}_chunk{chunk_idx}",
                "text": chunk_text,
                "source_id": doc["source_id"],
                "source_url": doc["source_url"],
                "source_type": doc["source_type"],
            })
    return chunks


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    print("=== Step 1: Ingesting documents ===")
    docs = ingest_all()
    print(f"\nTotal documents after cleaning: {len(docs)}")

    print("\n=== Step 2: Chunking ===")
    chunks = chunk_documents(docs)
    print(f"Total chunks produced: {len(chunks)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"\nChunks saved to {OUTPUT_PATH}")

    lengths = [len(c["text"]) for c in chunks]
    print(f"\nChunk length stats (characters):")
    print(f"  min={min(lengths)}  max={max(lengths)}  avg={sum(lengths)//len(lengths)}")


if __name__ == "__main__":
    main()
