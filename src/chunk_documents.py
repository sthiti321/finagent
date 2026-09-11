import os
import json
import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nfl@localhost:5432/finagent_rag"
)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_chunks():
    conn = psycopg.connect(DATABASE_URL)

    with conn.cursor() as cur:

        cur.execute("""
            SELECT document_id, title, file_path
            FROM documents
            ORDER BY document_id;
        """)

        documents = cur.fetchall()

        total_chunks = 0

        for document_id, title, file_path in documents:

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            chunks = chunk_text(content)

            for index, chunk in enumerate(chunks):

                cur.execute(
                    """
                    INSERT INTO document_chunks
                    (document_id, chunk_index, content, metadata)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        document_id,
                        index,
                        chunk,
                        json.dumps({
                            "title": title,
                            "source": file_path
                        })
                    )
                )

                total_chunks += 1

            print(f"{title}: {len(chunks)} chunks")

    conn.commit()
    conn.close()

    print(f"\nChunking completed.")
    print(f"Total chunks created: {total_chunks}")


if __name__ == "__main__":
    create_chunks()
