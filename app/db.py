"""
app/db.py
=========
Database module — PostgreSQL connection and schema initialisation.

Responsibilities:
    • get_connection()  →  return a live psycopg2 connection
    • init_db()         →  create extension, table, and HNSW index if missing
    • reset_db()        →  drop and recreate everything (use with caution!)
"""

import os
import logging
import psycopg2
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────────────────────────────────────

def get_connection():
    """Open and return a new psycopg2 database connection."""
    try:
        conn = psycopg2.connect(
            dbname   = os.getenv("DB_NAME"),
            user     = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host     = os.getenv("DB_HOST", "localhost"),
            port     = os.getenv("DB_PORT", "5432"),
        )
        return conn
    except Exception as exc:
        logger.error(f"Database connection failed: {exc}")
        raise

# ─────────────────────────────────────────────────────────────────────────────
# Schema initialisation (safe — never drops existing data)
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    """
    Create the pgvector extension, documents table, and HNSW index
    if they do not already exist.  Existing data is NEVER dropped.
    """
    conn = get_connection()
    cur  = conn.cursor()

    # 1. Enable pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create documents table (preserves existing rows)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id        SERIAL PRIMARY KEY,
            content   TEXT        NOT NULL,
            embedding VECTOR(768)
        );
    """)

    # 3. Create HNSW index for fast cosine-similarity search
    cur.execute("""
        CREATE INDEX IF NOT EXISTS documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops);
    """)

    conn.commit()
    cur.close()
    conn.close()
    logger.info("Database initialised successfully.")

# ─────────────────────────────────────────────────────────────────────────────
# Hard reset (drops ALL stored documents — use only when starting fresh)
# ─────────────────────────────────────────────────────────────────────────────

def reset_db():
    """
    WARNING: permanently deletes all documents and embeddings.
    Drops and recreates the documents table and HNSW index.
    """
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("DROP INDEX IF EXISTS documents_embedding_idx;")
    cur.execute("DROP TABLE IF EXISTS documents;")

    cur.execute("""
        CREATE TABLE documents (
            id        SERIAL PRIMARY KEY,
            content   TEXT        NOT NULL,
            embedding VECTOR(768)
        );
    """)

    cur.execute("""
        CREATE INDEX documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops);
    """)

    conn.commit()
    cur.close()
    conn.close()
    logger.info("Database reset complete — all previous data deleted.")
