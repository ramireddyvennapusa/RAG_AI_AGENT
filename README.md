# RAG AI Agent (Terminal CLI)

A fast, interactive Retrieval-Augmented Generation (RAG) AI Agent built entirely for the command line. This project lets you interactively ask questions based on your own documents and knowledge base directly from the terminal, powered by PostgreSQL with pgvector for fast semantic search and supported by multiple LLM backends (Ollama/LangChain or Google Gemini).

No web servers, no frontend dependencies—just raw speed and a clean command-line interface.

## 🌟 Features

- **Bring Your Own Data**: Easily ingest text, PDFs, and Word documents via the `add_data.py` script.
- **pgvector Integration**: Uses strict HNSW (Hierarchical Navigable Small World) indexing on PostgreSQL to perform lightning-fast similarity search over your document embeddings.
- **Multiple AI Backends**: 
  - Works fully locally using [Ollama](https://ollama.com/) (e.g., `phi3:mini`, `llama3`).
  - Supports [Google Gemini](https://ai.google.dev/) API.
- **Interactive CLI**: Simple and intuitive interactive prompt loop that lets you drill down with questions and gives you fast, streaming-style feedback.

## 🛠️ Prerequisites

Before you start, make sure you have the following installed on your system:

1. **Python 3.10+**
2. **PostgreSQL** (with the `pgvector` extension enabled)
3. **Ollama** (Optional, but required if you want to run completely local open-source models)

## 🚀 Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repository-url>
   cd rag_agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare the database**:
   Make sure your PostgreSQL daemon is running. You must create a database and install pgvector. For example, via `psql`:
   ```sql
   CREATE DATABASE testdb;
   \c testdb;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## ⚙️ Configuration

Create a `.env` file in the root directory (alongside `requirements.txt`). You can customize the behavior of the agent by setting the following environment variables:

```ini
# --- Database Configuration ---
DB_NAME=testdb
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# --- AI Backend Choice ---
# Supported options: 'ollama' or 'gemini'
LLM_BACKEND=ollama

# --- Ollama Configuration (If LLM_BACKEND=ollama) ---
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# --- Gemini Configuration (If LLM_BACKEND=gemini) ---
GEMINI_API_KEY=your_gemini_api_key
```

## 📖 Usage

### 1. Ingesting Documents (Knowledge Base)

Before the agent can answer anything, it needs data.

1. Create a folder named `data` in the root of the project.
2. Drop your supported documents (`.txt`, `.pdf`, etc.) into the `data` folder.
3. Run the ingestion script:
   ```bash
   python add_data.py
   ```
   > **Note:** The script will read the files, chunk them, generate embeddings using your chosen backend, and store them securely inside PostgreSQL.

### 2. Running the Agent Interface

Start the interactive terminal interface:

```bash
python -m app.main
```

The script will:
- Validate your environment variables.
- Connect to and initialize your pgvector indexes.
- Verify your connection to the specific AI backend.
- Drop you directly into a responsive CLI prompt (`>`).

**Example Session:**
```text
  STEP 5  Starting Interactive CLI

  ┌─────────────────────────────────────────────────┐
  │                                                 │
  │   Backend  →  Ollama / LangChain  [phi3:mini]   │
  │   Type your question and press Enter.           │
  │   Type 'exit' or 'quit' to stop.                │
  │                                                 │
  └─────────────────────────────────────────────────┘

> What is discussed in the sample document?

  [Retrieving context...]
  [Generating answer...]

  Based on the provided document, ...

> exit
  Goodbye!
```

## 📂 Project Structure

```text
rag_agent/
├── app/
│   ├── db.py                 # PostgreSQL connection & pgvector config
│   ├── embeddings.py         # Embedding generation logic
│   ├── generator.py          # Gemini AI answer generation logic
│   ├── langchain_generator.py # Ollama AI answer generation logic
│   ├── ingest.py             # Document reading & chunking core module
│   ├── retriever.py          # pgvector similarity search logic
│   └── main.py               # The main entrypoint and interactive CLI CLI
├── data/                     # Drop your documents here
├── .env                      # Secrets & configurations
├── add_data.py               # Script to ingest files
└── requirements.txt          # Python dependencies
```

## 📜 License

This project is licensed under the MIT License.
