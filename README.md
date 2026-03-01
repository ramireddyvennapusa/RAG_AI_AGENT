# RAG AI AGENT

> A fully local, terminal-based AI that answers questions from **your own documents** — no cloud, no frontend, just a clean command-line experience.

Built with **PostgreSQL + pgvector** for semantic search, **LangChain + Ollama** for local AI inference, and **Google Gemini** as an optional cloud backend.

---

## How It Works

```
Your Documents  →  add_data.py  →  Embeddings  →  PostgreSQL (pgvector)
                                                          ↓
Your Question   →  app/main.py  →  Vector Search  →  LLM (Ollama / Gemini)  →  Answer
```

1. **Ingest:** Your documents are read, split into chunks, and stored as vector embeddings in PostgreSQL.
2. **Ask:** When you type a question, it is embedded and matched against your stored chunks using cosine similarity.
3. **Answer:** The top matching chunks are passed as context to the LLM, which generates a grounded answer.

---

## Features

- **Broad file support** — PDF, DOCX, PPTX, XLSX, CSV, JSON, TXT, Markdown, HTML, and 30+ code file types
- **Fully local option** — Run with Ollama (e.g. `phi3:mini`, `llama3`) with zero data leaving your machine
- **Cloud option** — Switch to Google Gemini API with a single env variable change
- **Fast semantic search** — HNSW index on pgvector for sub-millisecond nearest-neighbour lookups
- **Interactive CLI** — Simple `>` prompt to keep asking questions in a single session
- **GUI file picker** — Run `python add_data.py` with no arguments to open a native file picker

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| PostgreSQL | With the `pgvector` extension installed |
| Ollama | Only needed if using `LLM_BACKEND=ollama` |
| Gemini API Key | Only needed if using `LLM_BACKEND=gemini` |

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/ramireddyvennapusa/RAG_AI_AGENT.git
cd RAG_AI_AGENT
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your PostgreSQL database**

In `psql`, create a database and enable pgvector:
```sql
CREATE DATABASE testdb;
\c testdb
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Configuration

Create a `.env` file in the project root (it is ignored by Git so your secrets stay safe):

```ini
# ── Database ────────────────────────────────────────
DB_NAME=testdb
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# ── AI Backend: choose 'ollama' or 'gemini' ─────────
LLM_BACKEND=ollama

# ── Ollama (local, no API key needed) ───────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# ── Gemini (cloud, requires API key) ────────────────
GEMINI_API_KEY=your_gemini_api_key
```

---

## Usage

### Step 1 — Ingest your documents

You have three options:

```bash
# Option A: GUI file picker (opens a native dialog to select files)
python add_data.py

# Option B: Pass specific files directly
python add_data.py report.pdf notes.txt

# Option C: Ingest an entire folder
python add_data.py --folder ./my_docs

# Option C (recursive): Include all subfolders too
python add_data.py --folder ./my_docs --recursive
```

### Step 2 — Run the agent

```bash
python -m app.main
```

The agent will validate your config, connect to the database, verify your AI backend, and then drop you into the interactive prompt:

```
  ╔══════════════════════════════════════════════════╗
  ║          RAG AI Agent  —  Starting Up            ║
  ╚══════════════════════════════════════════════════╝

  STEP 1  Loading environment variables ...  ✔
  STEP 2  Validating configuration      ...  ✔
  STEP 3  Initialising database         ...  ✔
  STEP 4  Checking AI backend           ...  ✔
  STEP 5  Starting Interactive CLI

  ┌─────────────────────────────────────────────────┐
  │   Backend  →  Ollama / LangChain  [phi3:mini]   │
  │   Type your question and press Enter.           │
  │   Type 'exit' or 'quit' to stop.                │
  └─────────────────────────────────────────────────┘

> What is this document about?

  [Retrieving context...]
  [Generating answer...]

  Based on the provided context, this document is about ...

> exit

  Goodbye!
```

---

## Supported File Types

| Category | Extensions |
|---|---|
| Documents | `.pdf` `.docx` `.pptx` `.xlsx` `.odt` |
| Text / Markdown | `.txt` `.md` `.rst` `.log` |
| Code | `.py` `.js` `.ts` `.java` `.cpp` `.c` `.cs` `.go` `.rb` `.php` `.sql` `.sh` |
| Data | `.csv` `.json` `.jsonl` |
| Web | `.html` `.htm` `.xml` |
| Config | `.yaml` `.yml` `.toml` `.ini` `.cfg` |

---

## Project Structure

```
RAG_AI_AGENT/
├── app/
│   ├── main.py                 # Entry point + interactive CLI loop
│   ├── db.py                   # PostgreSQL connection & table/index init
│   ├── embeddings.py           # Embedding generation (Gemini API)
│   ├── retriever.py            # pgvector cosine-similarity search
│   ├── langchain_generator.py  # Answer generation via Ollama + LangChain
│   └── generator.py            # Answer generation via Google Gemini
├── add_data.py                 # Universal document ingestion script
├── .env                        # Your secrets (not committed to Git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## License

This project is licensed under the **MIT License**.