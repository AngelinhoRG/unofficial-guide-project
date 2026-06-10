"""
embed.py — Milestone 4: Embedding + vector store + retrieval

Pipeline stage:
  documents/chunks.json  →  SentenceTransformer (all-MiniLM-L6-v2)
                         →  ChromaDB (local persistent collection)
                         →  retrieve(query, k=4) → top-k chunks + metadata

Run once to build the index:
    python3 embed.py --build

Test retrieval interactively:
    python3 embed.py --query "How many hours per week do CS students study?"
"""

import argparse
import json
import os

import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config — matches planning.md Retrieval Approach section
# ---------------------------------------------------------------------------

CHUNKS_PATH   = os.path.join("documents", "chunks.json")
CHROMA_DIR    = os.path.join("documents", "chroma_db")
COLLECTION    = "unofficial_guide"
EMBED_MODEL   = "all-MiniLM-L6-v2"
TOP_K         = 4

# ---------------------------------------------------------------------------
# Build: embed all chunks and persist to ChromaDB
# ---------------------------------------------------------------------------

def build_index():
    print(f"Loading chunks from {CHUNKS_PATH} ...")
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"  {len(chunks)} chunks loaded")

    print(f"\nLoading embedding model: {EMBED_MODEL} ...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Embedding chunks (this may take a minute) ...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    print(f"  Embeddings shape: {embeddings.shape}")  # (n_chunks, 384)

    print(f"\nStoring in ChromaDB at {CHROMA_DIR} ...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection so re-runs start fresh
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},  # cosine similarity, per planning.md
    )

    # ChromaDB requires ids as strings; use the chunk_id field
    ids        = [c["chunk_id"]   for c in chunks]
    metadatas  = [
        {
            "source_id":   str(c["source_id"]),
            "source_url":  c["source_url"],
            "source_type": c["source_type"],
        }
        for c in chunks
    ]

    # ChromaDB add() has a 5 461-item limit per call — batch to be safe
    BATCH = 500
    for start in range(0, len(chunks), BATCH):
        end = start + BATCH
        collection.add(
            ids        = ids[start:end],
            embeddings = embeddings[start:end].tolist(),
            documents  = texts[start:end],
            metadatas  = metadatas[start:end],
        )
        print(f"  Stored batch {start}–{end}")

    print(f"\nIndex built. {collection.count()} vectors in collection '{COLLECTION}'.")


# ---------------------------------------------------------------------------
# Retrieve: embed a query and return top-k chunks
# ---------------------------------------------------------------------------

def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    model  = SentenceTransformer(EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION)

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    # Flatten ChromaDB's nested-list response into a clean list of dicts
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text":        doc,
            "source_url":  meta["source_url"],
            "source_type": meta["source_type"],
            "source_id":   meta["source_id"],
            "distance":    round(dist, 4),
        })
    return hits


# ---------------------------------------------------------------------------
# Test: run evaluation plan queries and print results
# ---------------------------------------------------------------------------

EVAL_QUERIES = [
    "How many hours per week do CS students typically spend on coursework outside of class?",
    "How many hours per week do students say the OMS Central Machine Learning course requires?",
    "What strategies do CS students on Reddit recommend for managing a heavy course workload?",
]

def run_eval():
    for query in EVAL_QUERIES:
        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print('='*70)
        hits = retrieve(query)
        for i, hit in enumerate(hits, 1):
            print(f"\n  Result {i} | distance={hit['distance']} | {hit['source_type']} | source_id={hit['source_id']}")
            print(f"  URL: {hit['source_url']}")
            print(f"  {hit['text'][:400]}")
            if len(hit['text']) > 400:
                print("  [... truncated]")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="Embed chunks and build ChromaDB index")
    parser.add_argument("--eval",  action="store_true", help="Run evaluation plan queries")
    parser.add_argument("--query", type=str,            help="Run a single retrieval query")
    args = parser.parse_args()

    if args.build:
        build_index()
    if args.eval:
        run_eval()
    if args.query:
        print(f"\nQUERY: {args.query}\n")
        hits = retrieve(args.query)
        for i, hit in enumerate(hits, 1):
            print(f"Result {i} | distance={hit['distance']} | {hit['source_type']} | source_id={hit['source_id']}")
            print(f"URL: {hit['source_url']}")
            print(hit['text'])
            print()
    if not any([args.build, args.eval, args.query]):
        parser.print_help()
