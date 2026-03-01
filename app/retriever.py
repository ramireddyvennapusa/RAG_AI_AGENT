"""
app/retriever.py
================
Retrieval module — finds the most relevant document chunks from the
database for a given user query using pgvector cosine-similarity search.

Process:
    1. Embed the user's query  →  768-dim vector  (via Gemini API)
    2. Run a nearest-neighbour query against the documents table
    3. Return the top-K matching text chunks
"""

import logging
from app.db import get_connection
from app.embeddings import get_embedding

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def retrieve(query: str, top_k: int = 3) -> list[str]:
    """
    Return the top-K most relevant document chunks for the given query.

    Args:
        query:  The user's natural-language question.
        top_k:  Number of chunks to return (default: 3).

    Returns:
        A list of text strings (document chunks), ordered by relevance.
    """
    # Step 1 — Embed the query
    query_vector = get_embedding(query)

    # Step 2 — Format the vector as a PostgreSQL-compatible string
    #           e.g. "[0.12, -0.34, ...]"  cast to ::vector for pgvector
    emb_str = "[" + ",".join(str(v) for v in query_vector) + "]"

    # Step 3 — Run nearest-neighbour search using the <-> cosine-distance op
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT content
        FROM   documents
        ORDER  BY embedding <-> %s::vector
        LIMIT  %s;
    """, (emb_str, top_k))

    results = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    logger.info(f"Retrieved {len(results)} chunk(s) for query: '{query[:60]}…'")
    return results
