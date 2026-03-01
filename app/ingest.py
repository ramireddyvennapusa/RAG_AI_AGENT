import logging
from app.db import get_connection
from app.embeddings import get_embedding

logging.basicConfig(level=logging.INFO)

def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_documents():
    sample_docs = [
        "PostgreSQL is an advanced open-source relational database.",
        "pgvector enables vector similarity search inside PostgreSQL.",
        "Retrieval Augmented Generation combines search with LLM generation."
    ]

    conn = get_connection()
    cur = conn.cursor()

    for doc in sample_docs:
        chunks = chunk_text(doc)

        for chunk in chunks:
            embedding = get_embedding(chunk)

            cur.execute(
                "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
                (chunk, embedding)
            )

    conn.commit()
    cur.close()
    conn.close()
    logging.info("Documents ingested successfully.")
