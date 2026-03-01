"""
app/langchain_generator.py
==========================
LangChain + Ollama answer generator — uses a locally running Ollama LLM
to generate answers grounded in the retrieved document context.

Used when:  LLM_BACKEND=ollama  (default, set in .env)

Process:
    1. Build a LangChain LCEL chain: PromptTemplate → OllamaLLM → StrOutputParser
    2. On each call, combine context chunks and invoke the chain
    3. Return the stripped text response

No API key required — Ollama runs entirely on your local machine.
"""

import os
import logging
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Config (read from .env)
# ─────────────────────────────────────────────────────────────────────────────
_OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL",    "phi3:mini")

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Define the RAG prompt template
# ─────────────────────────────────────────────────────────────────────────────
_RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""\
You are a helpful AI assistant.

Answer ONLY from the context below.
If the answer is not found in the context, say "I don't know."

Context:
{context}

Question:
{question}

Answer:""",
)

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Build the LangChain LCEL chain (once at import time)
#          Chain: prompt → Ollama LLM → string parser
# ─────────────────────────────────────────────────────────────────────────────
def _build_chain():
    llm = OllamaLLM(
        base_url    = _OLLAMA_URL,
        model       = _OLLAMA_MODEL,
        temperature = 0.2,
        num_ctx     = 2048,    # Limits context window to reduce RAM usage
    )
    return _RAG_PROMPT | llm | StrOutputParser()

_chain = _build_chain()

# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_answer_langchain(query: str, context_chunks: list[str]) -> str:
    """
    Generate an answer using LangChain + a local Ollama model.

    Args:
        query:          The user's question.
        context_chunks: List of relevant text chunks from the retriever.

    Returns:
        A string answer from the local LLM, grounded in the context.
    """
    # Step 3 — Combine context chunks and invoke the chain
    context = "\n\n".join(context_chunks)
    try:
        answer = _chain.invoke({"context": context, "question": query})
        return answer.strip()
    except Exception as exc:
        logger.error(f"LangChain / Ollama generation error: {exc}")
        raise
