"""
app/generator.py
================
Gemini answer generator — uses Google's Gemini API to generate
an answer grounded in the retrieved document context.

Used when:  LLM_BACKEND=gemini  (set in .env)

Process:
    1. Combine retrieved context chunks into one block
    2. Build a RAG prompt (context + question)
    3. Call Gemini API and return the text response
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
_MODEL  = "gemini-2.0-flash"

# ─────────────────────────────────────────────────────────────────────────────
# RAG prompt template
# ─────────────────────────────────────────────────────────────────────────────
_PROMPT_TEMPLATE = """\
You are a helpful AI assistant.

Answer ONLY from the context below.
If the answer is not found in the context, say "I don't know."

Context:
{context}

Question:
{question}

Answer:"""

# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_answer(query: str, context_chunks: list[str]) -> str:
    """
    Generate an answer using the Gemini API.

    Args:
        query:          The user's question.
        context_chunks: List of relevant text chunks from the retriever.

    Returns:
        A string answer from Gemini, grounded in the context.
    """
    # Step 1 — Combine chunks into a single context block
    context = "\n\n".join(context_chunks)

    # Step 2 — Build the prompt
    prompt = _PROMPT_TEMPLATE.format(context=context, question=query)

    # Step 3 — Call Gemini and return the response
    try:
        response = _client.models.generate_content(
            model    = _MODEL,
            contents = prompt,
        )
        return response.text.strip()
    except Exception as exc:
        logger.error(f"Gemini generation error: {exc}")
        raise
