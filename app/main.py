"""
app/main.py
===========
MAIN ENTRY POINT — Run this file to start the RAG AI Agent.

    python app/main.py

Steps executed automatically:
    Step 1  Load environment variables from .env
    Step 2  Validate required configuration
    Step 3  Initialise the database (PostgreSQL + pgvector)
    Step 4  Check Ollama / AI backend connection
    Step 5  Start the web server  →  http://localhost:8000
"""

import os
import sys
import pathlib

# ── Make sure the project root is on sys.path so `app.*` imports work ─────────
ROOT = pathlib.Path(__file__).parent.parent          # rag_agent/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Fix Unicode output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
# Print helpers
# ─────────────────────────────────────────────────────────────────────────────

def banner():
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║          RAG AI Agent  —  Starting Up            ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()

def step_start(n: int, title: str):
    print(f"  STEP {n}  {title}")

def step_ok(msg: str):
    print(f"          ✔  {msg}")

def step_warn(msg: str):
    print(f"          ⚠  {msg}")

def step_fail(msg: str):
    print(f"\n  ✘  FAILED: {msg}")
    print("     Fix the issue above and try again.\n")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Load environment variables
# ─────────────────────────────────────────────────────────────────────────────
banner()
step_start(1, "Loading environment variables")

from dotenv import load_dotenv
env_file = ROOT / ".env"
if not env_file.exists():
    step_fail(f".env file not found at {env_file}\n"
              "     Create it with DB_NAME, DB_USER, DB_PASSWORD, etc.")
load_dotenv(dotenv_path=env_file)
step_ok(f".env loaded  ({env_file})")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Validate required configuration
# ─────────────────────────────────────────────────────────────────────────────
step_start(2, "Validating configuration")

BACKEND      = os.getenv("LLM_BACKEND", "ollama").lower()
DB_NAME      = os.getenv("DB_NAME")
DB_USER      = os.getenv("DB_USER")
DB_PASSWORD  = os.getenv("DB_PASSWORD")
DB_HOST      = os.getenv("DB_HOST", "localhost")
DB_PORT      = os.getenv("DB_PORT", "5432")
OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
GEMINI_KEY   = os.getenv("GEMINI_API_KEY")

missing = []
if not DB_NAME:    missing.append("DB_NAME")
if not DB_USER:    missing.append("DB_USER")
if not DB_PASSWORD: missing.append("DB_PASSWORD")
if BACKEND == "gemini" and not GEMINI_KEY:
    missing.append("GEMINI_API_KEY")

if missing:
    step_fail(f"Missing required .env values: {', '.join(missing)}")

BACKEND_LABEL = (
    f"Ollama / LangChain  [{OLLAMA_MODEL}]"
    if BACKEND == "ollama"
    else "Gemini (Google)"
)
step_ok(f"Backend  =  {BACKEND_LABEL}")
step_ok(f"Database =  {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Initialise the database
# ─────────────────────────────────────────────────────────────────────────────
step_start(3, "Initialising database  (PostgreSQL + pgvector)")

try:
    from app.db import init_db
    init_db()
    step_ok("Tables and HNSW index are ready")
except Exception as exc:
    step_fail(
        f"Cannot connect to PostgreSQL: {exc}\n\n"
        "     Checklist:\n"
        "       • Is PostgreSQL running?\n"
        "       • Are DB_HOST / DB_PORT / DB_USER / DB_PASSWORD correct in .env?\n"
        "       • Is the pgvector extension installed in your database?"
    )

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Check AI backend connection
# ─────────────────────────────────────────────────────────────────────────────
step_start(4, f"Checking AI backend connection  ({BACKEND_LABEL})")

if BACKEND == "ollama":
    import urllib.request, urllib.error
    try:
        with urllib.request.urlopen(OLLAMA_URL, timeout=4) as r:
            step_ok(f"Ollama is reachable at {OLLAMA_URL}")
            step_ok(f"Model in use: {OLLAMA_MODEL}")
    except (urllib.error.URLError, OSError):
        step_warn(f"Ollama is NOT reachable at {OLLAMA_URL}")
        step_warn("Run 'ollama serve' in a separate terminal, then ask questions.")
else:
    if GEMINI_KEY:
        step_ok("Gemini API key found")
    else:
        step_warn("GEMINI_API_KEY is missing — Gemini calls will fail")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Start Interactive CLI
# ─────────────────────────────────────────────────────────────────────────────
step_start(5, "Starting Interactive CLI")
print()
print(f"  ┌─────────────────────────────────────────────────┐")
print(f"  │                                                 │")
print(f"  │   Backend  →  {BACKEND_LABEL:<33} │")
print(f"  │   Type your question and press Enter.           │")
print(f"  │   Type 'exit' or 'quit' to stop.                │")
print(f"  │                                                 │")
print(f"  └─────────────────────────────────────────────────┘")
print()

if BACKEND == "gemini":
    from app.generator import generate_answer as _generate
else:
    from app.langchain_generator import generate_answer_langchain as _generate

from app.retriever import retrieve

def run_loop():
    while True:
        try:
            question = input("\n> ")
            if not question.strip():
                continue
            if question.strip().lower() in ['exit', 'quit']:
                print("\n  Goodbye!\n")
                break
                
            print("\n  [Retrieving context...]")
            context_chunks = retrieve(question.strip())
            
            if not context_chunks:
                print("\n  I don't have any relevant documents to answer that.")
                print("  Please add documents first by running:  python add_data.py")
                continue
                
            print("  [Generating answer...]\n")
            answer = _generate(question.strip(), context_chunks)
            print("  " + answer.replace("\n", "\n  "))
            
        except KeyboardInterrupt:
            print("\n  Goodbye!\n")
            break
        except Exception as exc:
            print(f"\n  Error: {exc}")

if __name__ == "__main__":
    run_loop()
