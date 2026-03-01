"""
app/embeddings.py
=================
Embedding module — converts text into a 768-dimensional vector
using Google's Gemini Embedding model via the Gemini API.

Used by:
    • app/retriever.py  (embed the user's query)
    • add_data.py       (embed each document chunk before storing)
"""

import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Gemini client — loaded once at import time
# ─────────────────────────────────────────────────────────────────────────────
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding model and output dimension (must match the DB column: VECTOR(768))
_EMBED_MODEL = "models/gemini-embedding-001"
_DIMENSIONS  = 768

# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_embedding(text: str) -> list[float]:
    """
    Return a 768-dim float list representing the semantic meaning of `text`.

    Args:
        text:  The text string to embed (query or document chunk).

    Returns:
        A list of 768 floats (the embedding vector).

    Raises:
        Exception: if the Gemini API call fails.
    """
    try:
        response = _client.models.embed_content(
            model    = _EMBED_MODEL,
            contents = text,
            config   = {"output_dimensionality": _DIMENSIONS},
        )
        return response.embeddings[0].values
    except Exception as exc:
        logger.error(f"Embedding error: {exc}")
        raise
