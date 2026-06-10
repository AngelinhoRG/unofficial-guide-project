"""
generate.py — Milestone 5: Grounded generation via Groq API

Pipeline stage:
  user query → retrieve() (embed.py)
             → Groq llama-3.3-70b-versatile
             → grounded answer + programmatically-appended source list

Grounding is enforced two ways:
  1. System prompt explicitly forbids answering outside the provided documents.
  2. Source URLs are extracted from retrieval metadata — the LLM never generates them.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()

GROQ_MODEL  = "llama-3.3-70b-versatile"
MAX_TOKENS  = 512
TEMPERATURE = 0.2   # low temperature keeps the model close to the retrieved text

# ---------------------------------------------------------------------------
# Grounding system prompt — enforces, does not merely suggest
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful assistant for CS students. "
    "You answer questions ONLY using the documents provided to you in the user message. "
    "You must NOT draw on any outside knowledge, general facts about CS programs, "
    "or information from your training data. "
    "If the provided documents do not contain enough information to answer the question, "
    'respond with exactly: "I don\'t have enough information on that." '
    "Never fabricate statistics, quotes, or claims that are not explicitly present in the documents. "
    "Be specific and paraphrase the source material closely."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_context(hits: list[dict]) -> str:
    """Format retrieved chunks as a numbered document block for the prompt."""
    parts = []
    for i, hit in enumerate(hits, 1):
        parts.append(
            f"[Document {i}]\n"
            f"Source: {hit['source_url']}\n"
            f"Type: {hit['source_type']}\n\n"
            f"{hit['text']}"
        )
    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask(question: str, k: int = 4) -> dict:
    """
    End-to-end RAG call: retrieve → generate → return grounded answer + sources.

    Returns:
        {
            "answer":  str,          # LLM response grounded in retrieved text
            "sources": list[str],    # deduplicated source URLs from retrieval metadata
            "hits":    list[dict],   # raw retrieval results (text + metadata + distance)
        }
    """
    hits    = retrieve(question, k=k)
    context = _build_context(hits)

    user_message = (
        f"Documents:\n{context}\n\n"
        "---\n\n"
        f"Question: {question}\n\n"
        "Answer using ONLY the documents above. "
        'If the answer is not in the documents, say "I don\'t have enough information on that."'
    )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    answer = completion.choices[0].message.content.strip()

    # Source attribution is programmatically guaranteed — extracted from retrieval
    # metadata, never left to the LLM to generate.
    sources = list(dict.fromkeys(hit["source_url"] for hit in hits))

    return {"answer": answer, "sources": sources, "hits": hits}


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "How many hours per week do CS students typically spend on coursework?"
    )
    print(f"Query: {query}\n")
    result = ask(query)
    print(f"Answer:\n{result['answer']}\n")
    print("Sources:")
    for s in result["sources"]:
        print(f"  • {s}")
